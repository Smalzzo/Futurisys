from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import  PredictionLog, ErrorLog

try:
    import numpy as _np  # type: ignore
except Exception:  # pragma: no cover
    _np = None  # fallback if numpy not available at import time


def _to_jsonable(val: Any) -> Any:
    # Convertit récursivement les types non JSON (Decimal, numpy, datetime, etc.)
    if val is None:
        return None
    if isinstance(val, (str, bool, int, float)):
        return val
    if isinstance(val, Decimal):
        try:
            return float(val)
        except Exception:
            return str(val)
    if _np is not None and isinstance(val, (_np.generic,)):
        return _to_jsonable(val.item())
    if isinstance(val, (list, tuple, set)):
        return [_to_jsonable(v) for v in val]
    if isinstance(val, dict):
        return {str(k): _to_jsonable(v) for k, v in val.items()}
    if isinstance(val, datetime):
        return val.isoformat()
    # Dernier recours: stringifier
    return str(val)
def save_prediction_log(
    db: Session,
    *,
    endpoint: str,
    requested_by: Optional[str],
    employee_id: Optional[int],
    latency_ms: Optional[int],
    status: str,
    payload: Dict[str, Any],
    output: Dict[str, Any],
) -> PredictionLog:
    # Upsert par employee_id: si une ligne existe déjà, on l'écrase
    # Nettoyage des structures JSON pour éviter les erreurs (Decimal non sérialisable, numpy, ...)
    payload = _to_jsonable(payload)
    output = _to_jsonable(output)
    row = None
    if employee_id is not None:
        # Utilise first() pour éviter toute exception MultipleResultsFound si des doublons existent déjà
        row = (
            db.query(PredictionLog)
            .filter(PredictionLog.employee_id == employee_id)
            .order_by(PredictionLog.id.desc())
            .first()
        )
    if row is None:
        row = PredictionLog(
            endpoint=endpoint,
            requested_by=requested_by,
            employee_id=employee_id,
            latency_ms=latency_ms,
            status=status,
            payload=payload,
            output=output,
        )
        db.add(row)
    else:
        row.endpoint = endpoint
        row.requested_by = requested_by
        row.latency_ms = latency_ms
        row.status = status
        row.payload = payload
        row.output = output
    db.commit()
    db.refresh(row)
    return row

def get_prediction_log_by_employee_id(db: Session, *, employee_id: int) -> Optional[PredictionLog]:
    return (
        db.query(PredictionLog)
        .filter(PredictionLog.employee_id == employee_id)
        .order_by(PredictionLog.id.desc())
        .first()
    )

def save_error_log(
    db: Session,
    *,
    endpoint: Optional[str],
    http_status: Optional[int],
    error_class: Optional[str],
    error_message: Optional[str],
    context: Dict[str, Any],
) -> ErrorLog:
    row = ErrorLog(
        endpoint=endpoint,
        http_status=http_status,
        error_class=error_class,
        error_message=error_message,
        context=context,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
