from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_api_key
from app.db.session import get_db
from app.db.repository import get_prediction_log_by_employee_id

router = APIRouter()


@router.get("/logs/prediction/{employee_id}", dependencies=[Depends(get_api_key)])
def get_prediction_log(employee_id: int, db: Session = Depends(get_db)):
    """Retourne le dernier log de prédiction enregistré pour un employé.

    Args:
        employee_id: Identifiant utilisé pour filtrer les logs.
        db: Session SQLAlchemy injectée par FastAPI.

    Raises:
        HTTPException: Si aucun log n’existe pour l’identifiant donné.

    Returns:
        Dictionnaire avec le payload loggé et le résultat de la prédiction.
    """
    row = get_prediction_log_by_employee_id(db, employee_id=employee_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Aucun log pour employee_id={employee_id}")
    return {
        "employee_id": employee_id,
        "payload": row.payload,
        "pred_quitte_entreprise": row.output.get("pred_quitte_entreprise") if isinstance(row.output, dict) else None,
    }
