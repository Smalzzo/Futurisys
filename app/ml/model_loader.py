# app/ml/model_loader.py
import os
import joblib

MODEL_LOCAL = os.getenv("MODEL_LOCAL", "app/ml/model.pkl")
MODEL_REPO_ID = os.getenv("MODEL_REPO_ID", "sma-nas/Futurisys")
MODEL_FILENAME = os.getenv("MODEL_FILENAME", "model.pkl")

_model = None

def _download_from_hub(local_dir: str):
    """Download the model file from Hugging Face Hub into local_dir.

    Import huggingface_hub lazily so importing this module doesn't fail in
    environments where huggingface_hub isn't installed (e.g., some test runs).
    """
    try:
        from huggingface_hub import hf_hub_download
    except ImportError as exc:
        raise ImportError(
            "huggingface_hub is required to download the model from the Hub. "
            "Install it (pip install huggingface_hub) or set MODEL_LOCAL to a local path."
        ) from exc

    hf_hub_download(
        repo_id=MODEL_REPO_ID,
        filename=MODEL_FILENAME,
        local_dir=local_dir,
        local_dir_use_symlinks=False,
    )


def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_LOCAL):
            os.makedirs(os.path.dirname(MODEL_LOCAL), exist_ok=True)
            _download_from_hub(os.path.dirname(MODEL_LOCAL))
        _model = joblib.load(MODEL_LOCAL)
    return _model
