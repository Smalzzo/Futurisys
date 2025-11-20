import os
import joblib
import numpy as np
import pytest
from app.ml.serve import ModelService, SEUIL_FIXE

def test_model_service_fails_when_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("MODEL_PATH", str(tmp_path / "nope.pkl"))
    svc = ModelService(os.environ["MODEL_PATH"])
    try:
        svc.load()
    except FileNotFoundError:
        pass
    else:
        assert False, "Expected FileNotFoundError"


def test_model_service_load_and_predict_with_dummy_model(tmp_path, monkeypatch):
    """Test que ModelService peut charger un modèle et faire une prédiction"""
    # Créer un modèle dummy
    from sklearn.ensemble import RandomForestClassifier
    dummy_model = RandomForestClassifier(n_estimators=2, random_state=42)
    
    # Créer des données d'entraînement minimales
    X_train = np.random.rand(10, 5)
    y_train = np.random.randint(0, 2, 10)
    dummy_model.fit(X_train, y_train)
    
    # Sauvegarder le modèle
    model_path = tmp_path / "test_model.pkl"
    joblib.dump(dummy_model, model_path)
    
    # Tester ModelService
    monkeypatch.setenv("MODEL_PATH", str(model_path))
    svc = ModelService(str(model_path))
    svc.load()
    
    # Vérifier que le modèle est chargé
    assert svc.model is not None
    
    # Test predict_proba
    payload = {f"feature_{i}": 0.5 for i in range(5)}
    proba = svc.predict_proba(payload)
    assert isinstance(proba, (int, float))
    assert 0 <= proba <= 1
    
    # Test predict_label
    label = svc.predict_label(payload)
    assert label in {0, 1}


def test_model_service_predict_uses_threshold():
    """Test que predict_label utilise bien le seuil SEUIL_FIXE"""
    from unittest.mock import MagicMock
    
    svc = ModelService("dummy_path")
    
    # Mock predict_proba pour retourner une valeur contrôlée
    svc.predict_proba = MagicMock(return_value=0.3)
    assert svc.predict_label({}) == 1  # 0.3 >= 0.125930 (SEUIL_FIXE)
    
    svc.predict_proba = MagicMock(return_value=0.7)
    assert svc.predict_label({}) == 1
    
    svc.predict_proba = MagicMock(return_value=0.1)  # < SEUIL_FIXE
    assert svc.predict_label({}) == 0

