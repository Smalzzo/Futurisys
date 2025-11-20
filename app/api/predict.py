import time
import math
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.api.schemas import ALL_FEATURES, PredictIn, PredictionResponse
from app.api.deps import get_api_key
from app.db.session import get_db
from app.db.models import EmployeeFeatures as EmployeeORM
from app.ml.serve import model_service
from app.db.repository import save_prediction_log
import logging


EXPECTED_COLS = [
    "frequence_deplacement",
    "genre",
    "statut_marital",
    "departement",
    "poste",
    "heure_supplementaires",
    "domaine_etude",
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


router = APIRouter()


def _normalize_payload(d: Dict[str, Any]) -> Dict[str, Any]:
    """Nettoie les valeurs du payload et prépare les colonnes dérivées.

    Args:
        d: Dictionnaire brut issu du modèle Pydantic.

    Returns:
        Nouveau dictionnaire où les chaînes sont en majuscules, les booléens
        homogénéisés, et les chaînes vides remplacées par `None`.
    """
    out = dict(d)

    for k in [
        "genre",
        "statut_marital",
        "departement",
        "poste",
        "heure_supplementaires",
        "domaine_etude",
        "frequence_deplacement",
    ]:
        if k in out and isinstance(out[k], str):
            out[k] = out[k].strip().upper()

    if "heure_supplementaires" in out and isinstance(out["heure_supplementaires"], str):
        vv = out["heure_supplementaires"]
        if vv in {"OUI", "YES", "Y", "1", "TRUE"}:
            out["heure_supplementaires"] = "OUI"
        elif vv in {"NON", "NO", "N", "0", "FALSE"}:
            out["heure_supplementaires"] = "NON"

    for k, v in list(out.items()):
        if isinstance(v, str) and v.strip() == "":
            out[k] = None

    return out


@router.post("/predict", response_model=PredictionResponse, dependencies=[Depends(get_api_key)])
def predict(features: PredictIn, db: Session = Depends(get_db)) -> PredictionResponse:
    """Effectue une prédiction à partir du JSON envoyé par le client.

    Args:
        features: Payload validé par `PredictIn`.
        db: Session SQLAlchemy (utilisée pour journaliser la requête).

    Returns:
        `PredictionResponse` contenant l'identifiant et le label `OUI/NON`.
    """
    t0 = time.perf_counter()
    d = features.model_dump(exclude_none=True)
    d = _normalize_payload(d)

    a_ent = d.get("annees_dans_l_entreprise")
    a_tot = d.get("annee_experience_totale")
    d["anciennete_log"] = math.log(a_ent) if (isinstance(a_ent, (int, float)) and a_ent > 0) else None
    d["annee_experience_totale_log"] = (
        math.log(a_tot) if (isinstance(a_tot, (int, float)) and a_tot > 0) else None
    )
    Xro = {c: d.get(c, None) for c in EXPECTED_COLS}

    try:
        label_int = model_service.predict_label(Xro)
        pred_str = "OUI" if int(label_int) == 1 else "NON"
    except Exception as e:
        logging.getLogger(__name__).exception("Echec predict_label: %s", e)
        raise

    try:
        latency_ms = int((time.perf_counter() - t0) * 1000)
        save_prediction_log(
            db,
            endpoint="/predict",
            requested_by=None,
            employee_id=d.get("id_employee"),
            latency_ms=latency_ms,
            status="OK",
            payload=Xro,
            output={"pred_quitte_entreprise": pred_str},
        )
    except Exception as e:
        logging.warning("save_prediction_log failed on /predict: %s", e)

    return PredictionResponse(employee_id=d.get("id_employee"), pred_quitte_entreprise=pred_str)


@router.get("/health")
def health():
    """Endpoint de santé utilisé par les probes ou le monitoring."""
    return {"status Api": "ok"}


@router.get(
    "/predict/by-id/{employee_id}",
    response_model=PredictionResponse,
    dependencies=[Depends(get_api_key)],
)
def predict_by_id(employee_id: int = Path(..., ge=1), db: Session = Depends(get_db)) -> PredictionResponse:
    """Effectue une prédiction en lisant les features déjà stockées en base.

    Args:
        employee_id: Identifiant de l'employé dont on lit les features.
        db: Session SQLAlchemy pour lire `EmployeeFeatures` et sauver les logs.

    Returns:
        `PredictionResponse` identique à celui de `/predict`.

    Raises:
        HTTPException: Si aucune ligne de features n'est trouvée pour l'identifiant.
    """
    t0 = time.perf_counter()
    row: Optional[EmployeeORM] = (
        db.query(EmployeeORM).filter(EmployeeORM.id_employee == employee_id).one_or_none()
    )
    if row is None:
        raise HTTPException(status_code=422, detail=f"Aucune features trouvée pour employee_id='{employee_id}'")

    raw_dict: Dict[str, Any] = {col: getattr(row, col) for col in ALL_FEATURES}
    x: Dict[str, Any] = _normalize_payload(raw_dict)
    label_int: int = model_service.predict_label(x)
    pred_str = "OUI" if int(label_int) == 1 else "NON"

    try:
        latency_ms = int((time.perf_counter() - t0) * 1000)
        save_prediction_log(
            db,
            endpoint=f"/predict/by-id/{employee_id}",
            requested_by=None,
            employee_id=employee_id,
            latency_ms=latency_ms,
            status="OK",
            payload={"employee_id": employee_id, "features": x},
            output={"pred_quitte_entreprise": pred_str},
        )
    except Exception as e:
        logging.warning("save_prediction_log failed on /predict/by-id: %s", e)

    return PredictionResponse(employee_id=employee_id, pred_quitte_entreprise=pred_str)
