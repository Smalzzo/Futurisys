# app/ml/model_loader.py
import os
import logging
import joblib

# Prefer explicit MODEL_LOCAL, else fall back to MODEL_PATH for consistency with ModelService
MODEL_LOCAL = os.getenv("MODEL_LOCAL") or os.getenv("MODEL_PATH") or "app/ml/model.pkl"
MODEL_REPO_ID = os.getenv("MODEL_REPO_ID", "sma-nas/Futurisys")
MODEL_FILENAME = os.getenv("MODEL_FILENAME", "model.pkl")

_model = None
_logger = logging.getLogger(__name__)

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
            try:
                _download_from_hub(os.path.dirname(MODEL_LOCAL))
            except ImportError:
                # Graceful degrade: log and skip download. Let caller lazily load later.
                _logger.warning(
                    "huggingface_hub not installed; skipping Hub download. "
                    "Set MODEL_LOCAL/MODEL_PATH to an existing file or install huggingface_hub."
                )
                return None
        _model = joblib.load(MODEL_LOCAL)
    return _model
