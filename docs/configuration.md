# Configuration

## Variables d’environnement (principales)
- `API_KEY`: clé API attendue (en-tête `x-api-key`)
- `DATABASE_URL`: URL base (ex: `sqlite:///./ml_service.db` ou PostgreSQL)
- `MODEL_PATH`: chemin local du modèle (défaut `app/ml/model.pkl`)
- Hugging Face Hub (optionnel):
  - `MODEL_REPO_ID`, `MODEL_FILENAME`, `HF_TOKEN`

## Fichiers
- `.env`: variables locales
- `pyproject.toml`: packaging du projet
- `requirements.txt`: dépendances

