# app/schemas.py
from __future__ import annotations
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, ValidationError, ConfigDict, StrictInt
from pydantic import model_validator

# petit commantaire: ici on met les noms de colonnes
# on essaye de garder un ordre un peu logique par familles
COL_NUM = [
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
   "anciennete_log" ,
   "annee_experience_totale_log"
]
# colonnes qui sont des mots (categoriel)
COL_NOMINAL = [
    "genre",
    "statut_marital",
    "departement",
    "poste",
    "heure_supplementaires",
    "domaine_etude",
]
# une colonne ordinale (il y a un ordre)
COL_ORDINAL = ["frequence_deplacement"]

# toutes les features ensemble (util pour construire un dict complet)
ALL_FEATURES = COL_NUM + COL_NOMINAL + COL_ORDINAL


class PredictIn(BaseModel):
    # ici on dis a pydantic de refuser les champs inconnus
    # comme ça on evite les fautes de frappe dans le json
    model_config = ConfigDict(extra="forbid")
    
    # Identité requise et entière (doit etre un int stricte)
    id_employee: StrictInt = Field(..., description="Identifiant employé (entier)")

    # NUM
    age: Optional[float] = None
    nombre_experiences_precedentes: Optional[float] = None
    annees_dans_le_poste_actuel: Optional[float] = None
    satisfaction_employee_environnement: Optional[float] = None
    note_evaluation_precedente: Optional[float] = None
    niveau_hierarchique_poste: Optional[float] = None
    satisfaction_employee_nature_travail: Optional[float] = None
    satisfaction_employee_equipe: Optional[float] = None
    satisfaction_employee_equilibre_pro_perso: Optional[float] = None
    note_evaluation_actuelle: Optional[float] = None
    augementation_salaire_precedente: Optional[float] = None
    nombre_participation_pee: Optional[float] = None
    nb_formations_suivies: Optional[float] = None
    distance_domicile_travail: Optional[float] = None
    niveau_education: Optional[float] = None
    annees_depuis_la_derniere_promotion: Optional[float] = None
    annes_sous_responsable_actuel: Optional[float] = None
    annees_dans_l_entreprise: Optional[float] = None
    annee_experience_totale: Optional[float] = None

    # NOMINAL (textes)
    genre: Optional[str] = None
    statut_marital: Optional[str] = None
    departement: Optional[str] = None
    poste: Optional[str] = None
    heure_supplementaires: Optional[str] = None  
    domaine_etude: Optional[str] = None

    # ORDINAL (valeurs avec un ordre possible)
    frequence_deplacement: Optional[str] = None  

    # VALIDATION: ici on fait des petits nettoyages et verifs
    @field_validator("genre", "statut_marital", "departement", "poste", "domaine_etude", "frequence_deplacement", mode="before")
    @classmethod
    def normalize_upper_or_none(cls, v):
        # met en MAJ pour avoir une valeur propre, sinon None
        if v is None:
            return v
        s = str(v).strip()
        return s.upper() if s else None

    @field_validator("heure_supplementaires", mode="before")
    @classmethod
    def normalize_yes_no(cls, v):
        # converti les variantes yes/no vers OUI/NON
        # si pas reconnu -> on lève une erreur plus bas
        if v is None:
            return v
        s = str(v).strip().upper()
        if s in {"OUI", "YES", "Y", "1", "TRUE"}:
            return "OUI"
        if s in {"NON", "NO", "N", "0", "FALSE"}:
            return "NON"
        if not s:
            return None
        # Si une valeur non reconnue est fournie, refuser
        raise ValueError("heure_supplementaires doit être OUI ou NON")

    @field_validator("augementation_salaire_precedente", mode="before")
    @classmethod
    def coerce_pct(cls, v):
        # supporte "5%", " 5 % ", 5, "5" (on remplace la virgule)
        if v is None:
            return v
        if isinstance(v, (int, float)):
            return float(v)
        s = str(v).strip().replace("%", "").replace(",", ".")
        return float(s) if s else None

    @model_validator(mode="after")
    def validate_non_negative(self):
        # Refuse valeurs négatives pour les features numeriques
        # car c'est pas logique pour nos champs (ex: age)
        for name in COL_NUM + ["annees_dans_l_entreprise", "annee_experience_totale"]:
            if hasattr(self, name):
                val = getattr(self, name)
                if val is not None and isinstance(val, (int, float)) and val < 0:
                    raise ValueError(f"{name} ne peut pas être négatif")
        return self



class PredictionResponse(BaseModel):
    employee_id: Optional[int] = None
    pred_quitte_entreprise: Literal["OUI", "NON"]
