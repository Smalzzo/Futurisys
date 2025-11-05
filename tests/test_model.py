import os
import joblib
import numpy as np
from app.ml.serve import ModelService

def test_model_service_fails_when_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("MODEL_PATH", str(tmp_path / "nope.pkl"))
    svc = ModelService(os.environ["MODEL_PATH"])
    try:
        svc.load()
    except FileNotFoundError:
        pass
    else:
        assert False, "Expected FileNotFoundError"


