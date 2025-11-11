# ML Service (FastAPI + ML)

Bienvenue dans la documentation du service ML. Vous trouverez ici:
- L’API (endpoints, schémas, exemples)
- Le modèle (données, performances, maintenance)
- L’architecture et la configuration
- Le déploiement (Docker, Hugging Face Spaces, CI)

Liens rapides
- Swagger/OpenAPI: `/docs`
- Santé: `GET /api/v1/health`

## Prérequis
- Python 3.12
- FastAPI, Uvicorn, SQLAlchemy
- Modèle `model.pkl` accessible (fichier ou Hugging Face Hub)

## Installation rapide
```
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Sécurité
- En-tête requis: `x-api-key` (voir Configuration)

