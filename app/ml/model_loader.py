# app/ml/model_loader.py
import os
from huggingface_hub import hf_hub_download
import joblib

MODEL_LOCAL = os.getenv("MODEL_LOCAL", "app/ml/model.pkl")
MODEL_REPO_ID = os.getenv("MODEL_REPO_ID", "sma-nas/Futurisys") 
MODEL_FILENAME = os.getenv("MODEL_FILENAME", "model.pkl")

_model = None

def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_LOCAL):
            os.makedirs(os.path.dirname(MODEL_LOCAL), exist_ok=True)
            hf_hub_download(
                repo_id=MODEL_REPO_ID,
                filename=MODEL_FILENAME,
                local_dir=os.path.dirname(MODEL_LOCAL),
                local_dir_use_symlinks=False,
            )
        _model = joblib.load(MODEL_LOCAL)
    return _model
