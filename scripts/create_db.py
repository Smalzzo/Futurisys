import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

import psycopg
from sqlalchemy import create_engine, text

# Essayez d'utiliser la config + ORM de l'app (même DB / mêmes tables)
try:
    from app.core.config import get_settings
    from app.db.base import Base
    from app.db import models  # noqa: F401  (importe les modèles pour la metadata)
except Exception:  # pragma: no cover
    get_settings = None
    Base = None


HERE = Path(__file__).resolve().parent
DEFAULT_SQL_DIR = HERE.parent / "db"
DEFAULT_IMPORTS_DIR = HERE.parent / "imports"

_env_sql_dir = os.getenv("SQL_DIR")
SQL_DIR = Path(_env_sql_dir) if _env_sql_dir else DEFAULT_SQL_DIR

_env_imports_dir = os.getenv("IMPORTS_DIR")
IMPORTS_DIR = Path(_env_imports_dir) if _env_imports_dir else DEFAULT_IMPORTS_DIR

FILES = [
    "00_raw_employee.sql",
    "01_Import_csv.sql",
    "02_raw_employee_clean.sql",
    "03_mart_employee.sql",
    "04_mart_create_view.sql",
    "05_ml_logging.sql",
]


def lancesql(conn, sql_text: str):
    with conn.cursor() as cur:
        cur.execute(sql_text)
    conn.commit()


def _detect_backend() -> str:
    # Préfère Settings (lit .env), sinon env direct
    try:
        if get_settings is not None:
            url = get_settings().DATABASE_URL
            if url.startswith("sqlite:"):
                return "sqlite"
            return "postgres"
    except Exception:
        pass
    db_url = os.getenv("DATABASE_URL", "")
    if db_url.startswith("sqlite:"):
        return "sqlite"
    return "postgres"


def _sqlite_engine():
    assert get_settings is not None and Base is not None, "Settings/ORM indisponibles pour SQLite"
    url = get_settings().DATABASE_URL
    connect_args = {"check_same_thread": False} if url.startswith("sqlite:") else {}
    return create_engine(url, future=True, connect_args=connect_args)


def _upper_strip_series(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip().str.upper().replace({"": None})


def lancesqlite_Initialisation():
    print(f"[Initialisation_SQLITE] IMPORTS_DIR = {IMPORTS_DIR}")
    if not IMPORTS_DIR.exists():
        raise SystemExit(f"Dossier imports introuvable: {IMPORTS_DIR}")

    sirh_path = IMPORTS_DIR / "extrait_sirh.csv"
    eval_path = IMPORTS_DIR / "extrait_eval.csv"
    sond_path = IMPORTS_DIR / "extrait_sondage.csv"
    for p in (sirh_path, eval_path, sond_path):
        if not p.exists():
            raise SystemExit(f"Fichier manquant: {p}")

    # Chargement CSV
    sirh = pd.read_csv(sirh_path, encoding="utf-8")
    evaldf = pd.read_csv(eval_path, encoding="utf-8")
    sond = pd.read_csv(sond_path, encoding="utf-8")

    # SIRH: numériques + catégorielles en majuscules
    for col in [
        "id_employee",
        "age",
        "revenu_mensuel",
        "nombre_experiences_precedentes",
        "nombre_heures_travailless",
        "annee_experience_totale",
        "annees_dans_l_entreprise",
        "annees_dans_le_poste_actuel",
    ]:
        if col in sirh.columns:
            sirh[col] = pd.to_numeric(sirh[col], errors="coerce")
    for col in ["genre", "statut_marital", "departement", "poste"]:
        if col in sirh.columns:
            sirh[col] = _upper_strip_series(sirh[col])

    # EVAL: id_employee depuis eval_number + numériques + heure_supplementaires
    if "eval_number" in evaldf.columns:
        tmp = (
            evaldf["eval_number"].astype(str).str.upper().str.replace(" ", "")
            .str.replace(r"^\D+", "", regex=True)
        )
        evaldf["id_employee"] = pd.to_numeric(tmp, errors="coerce")
    for col in [
        "satisfaction_employee_environnement",
        "note_evaluation_precedente",
        "niveau_hierarchique_poste",
        "satisfaction_employee_nature_travail",
        "satisfaction_employee_equipe",
        "satisfaction_employee_equilibre_pro_perso",
        "note_evaluation_actuelle",
        "augementation_salaire_precedente",
    ]:
        if col in evaldf.columns:
            if col == "augementation_salaire_precedente":
                evaldf[col] = (
                    evaldf[col]
                    .astype(str)
                    .str.strip()
                    .str.replace("%", "")
                    .str.replace(",", ".")
                )
            evaldf[col] = pd.to_numeric(evaldf[col], errors="coerce")
    if "heure_supplementaires" in evaldf.columns:
        evaldf["heure_supplementaires"] = _upper_strip_series(evaldf["heure_supplementaires"])

    # SONDAGE: id depuis code_sondage + numériques + catégorielles
    if "code_sondage" in sond.columns:
        sond["id_employee"] = pd.to_numeric(
            sond["code_sondage"].astype(str).str.replace(" ", ""), errors="coerce"
        )
    for col in [
        "a_quitte_l_entreprise",
        "domaine_etude",
        "ayant_enfants",
        "frequence_deplacement",
    ]:
        if col in sond.columns:
            sond[col] = _upper_strip_series(sond[col])
    for col in [
        "nombre_participation_pee",
        "nb_formations_suivies",
        "nombre_employee_sous_responsabilite",
        "distance_domicile_travail",
        "niveau_education",
        "annees_depuis_la_derniere_promotion",
        "annes_sous_responsable_actuel",
    ]:
        if col in sond.columns:
            sond[col] = pd.to_numeric(sond[col], errors="coerce")

    # Jointures
    df = sirh.merge(evaldf, on="id_employee", how="left").merge(sond, on="id_employee", how="left")

    # Features dérivées (logs naturels > 0)
    def _log_pos(series: pd.Series) -> pd.Series:
        s = pd.to_numeric(series, errors="coerce")
        s = s.mask(~(s > 0))
        return np.log(s)

    if "annees_dans_l_entreprise" in df.columns:
        df["anciennete_log"] = _log_pos(df["annees_dans_l_entreprise"])
    else:
        df["anciennete_log"] = np.nan
    if "annee_experience_totale" in df.columns:
        df["annee_experience_totale_log"] = _log_pos(df["annee_experience_totale"])
    else:
        df["annee_experience_totale_log"] = np.nan

    # Colonnes cibles selon le modèle ORM EmployeeFeatures
    cols = [
        "id_employee",
        "a_quitte_l_entreprise",
        "age",
        "nombre_experiences_precedentes",
        "annees_dans_le_poste_actuel",
        "satisfaction_employee_environnement",
        "note_evaluation_precedente",
        "niveau_hierarchique_poste",
        "satisfaction_employee_nature_travail",
        "satisfaction_employee_equipe",
        "satisfaction_employee_equilibre_pro_perso",
        "note_evaluation_actuelle",
        "augementation_salaire_precedente",
        "nombre_participation_pee",
        "nb_formations_suivies",
        "distance_domicile_travail",
        "niveau_education",
        "annees_depuis_la_derniere_promotion",
        "annes_sous_responsable_actuel",
        "anciennete_log",
        "annee_experience_totale_log",
        "genre",
        "statut_marital",
        "departement",
        "poste",
        "heure_supplementaires",
        "domaine_etude",
        "frequence_deplacement",
    ]
    cols_presentes = [c for c in cols if c in df.columns]
    df_out = df[cols_presentes].copy()

    # Assure la conformité NOT NULL du schéma ORM SQLite
    # 1) id_employee non nul et entier
    if "id_employee" in df_out.columns:
        df_out = df_out[pd.notna(df_out["id_employee"])].copy()
        df_out["id_employee"] = pd.to_numeric(df_out["id_employee"], errors="coerce").fillna(0).astype(int)

    # 2) Remplissage des numériques manquants par 0
    num_cols = [
        "age",
        "nombre_experiences_precedentes",
        "annees_dans_le_poste_actuel",
        "satisfaction_employee_environnement",
        "note_evaluation_precedente",
        "niveau_hierarchique_poste",
        "satisfaction_employee_nature_travail",
        "satisfaction_employee_equipe",
        "satisfaction_employee_equilibre_pro_perso",
        "note_evaluation_actuelle",
        "augementation_salaire_precedente",
        "nombre_participation_pee",
        "nb_formations_suivies",
        "distance_domicile_travail",
        "niveau_education",
        "annees_depuis_la_derniere_promotion",
        "annes_sous_responsable_actuel",
        "anciennete_log",
        "annee_experience_totale_log",
    ]
    for c in num_cols:
        if c in df_out.columns:
            df_out[c] = pd.to_numeric(df_out[c], errors="coerce").fillna(0)

    # 3) Remplissage des catégorielles manquantes par chaîne vide (sera normalisée à None côté API)
    cat_cols = [
        "a_quitte_l_entreprise",
        "genre",
        "statut_marital",
        "departement",
        "poste",
        "heure_supplementaires",
        "domaine_etude",
        "frequence_deplacement",
    ]
    for c in cat_cols:
        if c in df_out.columns:
            df_out[c] = df_out[c].astype(object)
            df_out[c] = df_out[c].where(pd.notna(df_out[c]), "")

    # Écriture en base
    engine = _sqlite_engine()
    assert Base is not None
    # Recrée proprement les tables de logs pour garantir un PK auto-incrément compatible SQLite
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS prediction_log"))
        conn.execute(text("DROP TABLE IF EXISTS error_log"))
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM employee_features"))
    df_out.to_sql("employee_features", con=engine, if_exists="append", index=False)
    print(f"[Initialisation_SQLITE] {len(df_out)} lignes insérées dans employee_features")


def lancepostgres_Initialisation():
    print(f"[DEBUG] SQL_DIR = {SQL_DIR}")
    if not SQL_DIR.exists():
        raise SystemExit(
            f"Dossier SQL introuvable: {SQL_DIR} (définis SQL_DIR ou place les .sql dans {DEFAULT_SQL_DIR})"
        )
    print("[DEBUG] Contenu du dossier SQL:")
    for p in sorted(SQL_DIR.glob("*.sql")):
        print(" -", p.name)

    host = os.getenv("POSTGRES_HOST", "localhost")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    db = os.getenv("POSTGRES_DB", "mldb")
    user = os.getenv("POSTGRES_USER", "smail")
    pwd = os.getenv("POSTGRES_PASSWORD", "smail")

    conn_str = f"host={host} port={port} dbname={db} user={user} password={pwd}"
    with psycopg.connect(conn_str) as conn:
        for fname in FILES:
            path = SQL_DIR / fname
            if not path.exists():
                raise SystemExit(f"Missing SQL file: {path}")
            print(f"Running {path}...")
            sql = path.read_text(encoding="utf-8")
            lancesql(conn, sql)
    print("PostgreSQL database ready.")


def main():
    print(f"[DEBUG] cwd        = {Path.cwd()}")
    print(f"[DEBUG] script dir = {HERE}")
    backend = _detect_backend()
    print(f"[DEBUG] Backend    = {backend}")
    if backend == "sqlite":
        lancesqlite_Initialisation()
    else:
        lancepostgres_Initialisation()


if __name__ == "__main__":
    main()
