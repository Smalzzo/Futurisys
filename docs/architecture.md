# Architecture

## Composants
- API FastAPI: `app/main.py`, routes sous `app/api/`
- Accès base: SQLAlchemy (`app/db/`)
- Service ML: `app/ml/serve.py`
- Config: `app/core/config.py`

## Schéma logique
- Client → FastAPI (`/api/v1/...`) → Service ML (chargement du modèle) → Prédiction → Log en base

## Sécurité
- En-tête `x-api-key` vérifié par `app/api/deps.py`

