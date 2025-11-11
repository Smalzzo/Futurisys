from __future__ import annotations
from typing import Dict, Any
import os, joblib, numpy as np, pandas as pd
from sklearn.pipeline import Pipeline

POSITIVE = 1
SEUIL_FIXE = 0.125930
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(os.path.dirname(__file__), "model.pkl"))

class ModelService:
    def __init__(self, model_path: str = MODEL_PATH):
        self.model_path = model_path
        self.model: Pipeline | None = None

    def load(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        self.model = joblib.load(self.model_path)
        return self

    def _final_estimator(self):        
        if hasattr(self.model, "steps"):
            return self.model.steps[-1][1]
        return self.model

    

    def predict_proba(self, payload: Dict[str, Any]) -> float:
        if self.model is None:
            self.load()
        X = pd.DataFrame([payload])
        p = self.model.predict_proba(X)           
        estimator = self._final_estimator()             
        classes = getattr(estimator, "classes_", None)  
        idx = np.where(classes == POSITIVE)[0]
        if idx.size == 0:
            raise ValueError(f"Classe positive {POSITIVE!r} absente parmi {classes!r}.")
        return float(p[0, int(idx[0])])

    def predict_label(self, payload: Dict[str, Any]) -> int:        
        proba_pos = self.predict_proba(payload)
        return int(proba_pos >= SEUIL_FIXE)

model_service = ModelService()
