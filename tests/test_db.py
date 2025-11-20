"""Tests pour la couche DB (models, repository)"""
import pytest
from app.db.models import EmployeeFeatures, PredictionLog
from app.db.repository import save_prediction_log, _to_jsonable
from app.db.session import engine
from sqlalchemy.orm import Session
from datetime import datetime


def test_employee_features_model():
    """Test création d'un objet EmployeeFeatures"""
    emp = EmployeeFeatures(
        id_employee=1,
        age=30,
        genre="MASCULIN",
        statut_marital="MARIE",
        departement="VENTES",
    )
    assert emp.id_employee == 1
    assert emp.age == 30
    assert emp.genre == "MASCULIN"


def test_prediction_log_model():
    """Test création d'un objet PredictionLog"""
    log = PredictionLog(
        endpoint="/predict",
        employee_id=123,
        latency_ms=50,
        status="OK",
    )
    assert log.endpoint == "/predict"
    assert log.employee_id == 123
    assert log.latency_ms == 50
    assert log.status == "OK"


def test_to_jsonable_conversion():
    """Test conversion de valeurs en JSON-able"""
    import numpy as np
    
    # Test avec int numpy
    assert _to_jsonable(np.int64(42)) == 42
    assert _to_jsonable(np.float32(3.14)) == pytest.approx(3.14, rel=1e-2)
    
    # Test avec datetime
    dt = datetime(2025, 1, 1, 12, 0, 0)
    result = _to_jsonable(dt)
    assert isinstance(result, str)
    
    # Test avec None
    assert _to_jsonable(None) is None
    
    # Test avec dict
    d = {"a": np.int64(1), "b": 2}
    result = _to_jsonable(d)
    assert result == {"a": 1, "b": 2}
    
    # Test avec list
    lst = [np.int64(1), 2, "test"]
    result = _to_jsonable(lst)
    assert result == [1, 2, "test"]
