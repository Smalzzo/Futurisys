import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import psycopg
except ImportError:
    psycopg = None  # Optional for SQLite-only usage

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
    
    # Check if CSV files exist; if not, create dummy data
    sirh_path = IMPORTS_DIR / "extrait_sirh.csv"
    eval_path = IMPORTS_DIR / "extrait_eval.csv"
    sond_path = IMPORTS_DIR / "extrait_sondage.csv"
    
    csv_exists = sirh_path.exists() and eval_path.exists() and sond_path.exists()
    
    if not csv_exists:
        print("[Initialisation_SQLITE] CSV files not found; creating dummy data for testing...")
        # Create minimal dummy data
        sirh = pd.DataFrame({
            "id_employee": [1, 2, 3, 4, 5],
            "age": [30, 35, 40, 28, 45],
            "revenu_mensuel": [2000, 2500, 3000, 1800, 3500],
            "nombre_experiences_precedentes": [2, 3, 5, 1, 7],
            "nombre_heures_travailless": [35, 40, 40, 35, 40],
            "annee_experience_totale": [5, 8, 12, 3, 15],
            "annees_dans_l_entreprise": [3, 5, 8, 2, 10],
            "annees_dans_le_poste_actuel": [2, 3, 5, 1, 7],
            "genre": ["M", "F", "M", "F", "M"],
            "statut_marital": ["CELIBATAIRE", "MARIE", "CELIBATAIRE", "MARIE", "DIVORCE"],
            "departement": ["IT", "HR", "FINANCE", "IT", "OPERATIONS"],
            "poste": ["ENGINEER", "MANAGER", "ANALYST", "JUNIOR", "DIRECTOR"],
        })
        evaldf = pd.DataFrame({
            "eval_number": ["EMP001", "EMP002", "EMP003", "EMP004", "EMP005"],
            "id_employee": [1, 2, 3, 4, 5],
            "satisfaction_employee_environnement": [7, 8, 6, 9, 7],
            "note_evaluation_precedente": [3.5, 4.0, 3.8, 3.2, 4.2],
            "niveau_hierarchique_poste": [2, 3, 2, 1, 4],
            "satisfaction_employee_nature_travail": [7, 8, 7, 8, 9],
            "satisfaction_employee_equipe": [8, 7, 8, 9, 8],
            "satisfaction_employee_equilibre_pro_perso": [6, 7, 5, 8, 6],
            "note_evaluation_actuelle": [3.6, 4.1, 3.9, 3.5, 4.3],
            "augementation_salaire_precedente": ["5%", "3%", "4%", "2%", "6%"],
            "heure_supplementaires": ["OUI", "NON", "OUI", "NON", "NON"],
        })
        sond = pd.DataFrame({
            "code_sondage": ["EMP001", "EMP002", "EMP003", "EMP004", "EMP005"],
            "id_employee": [1, 2, 3, 4, 5],
            "a_quitte_l_entreprise": ["NON", "NON", "NON", "NON", "OUI"],
            "domaine_etude": ["INFORMATIQUE", "GESTION", "FINANCE", "INFORMATIQUE", "MANAGEMENT"],
            "ayant_enfants": ["OUI", "OUI", "NON", "OUI", "NON"],
            "frequence_deplacement": ["RAREMENT", "SOUVENT", "RAREMENT", "JAMAIS", "SOUVENT"],
            "nombre_participation_pee": [2, 1, 0, 3, 5],
            "nb_formations_suivies": [3, 2, 4, 1, 6],
            "nombre_employee_sous_responsabilite": [0, 5, 0, 0, 10],
            "distance_domicile_travail": [15, 25, 10, 30, 20],
            "niveau_education": [3, 4, 3, 2, 4],
            "annees_depuis_la_derniere_promotion": [1, 2, 3, 0, 4],
            "annes_sous_responsable_actuel": [2, 3, 0, 0, 8],
        })
    else:
        if not IMPORTS_DIR.exists():
            raise SystemExit(f"Dossier imports introuvable: {IMPORTS_DIR}")
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
    if psycopg is None:
        raise SystemExit("psycopg is required for PostgreSQL. Install it: pip install psycopg")
    
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
