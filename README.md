---
title: Futurisys ML Service
emoji: 🐍
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---


# ML Service POC (FastAPI + PostgreSQL)

POC de déploiement d'un modèle de machine learning via une API FastAPI, avec (PostgreSQL en dev) et (sqlite en prod) et tests Pytest + couverture.

Inialisation de la base au lancemeent du service

## 1. Structure


app/
  api/            # Schémas Pydantic, dépendances, routes
  core/           # Config
  db/             # SQLAlchemy
  ml/             # Chargement du modèle (model.pkl)
  main.py
scripts/
  create_db.py
tests/
.github/workflows/ci.yml
requirements.txt
.env.example


## 2. Démarrer

### DB

docker compose up -d
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/create_db.py


### API
Placer `app/ml/model.pkl` puis :

uvicorn app.main:app --reload

Docs: http://localhost:8000/docs

### Exemples

curl -H "x-api-key: change-me" -X POST http://localhost:8000/api/predict -H "Content-Type: application/json" -d '{"age":35,"revenu_mensuel":2600,"poste":"Dev"}'
curl -H "x-api-key: change-me" http://localhost:8000/api/predict/by-id/EMP001


## 3. Tests

pytest --cov=app --cov-report=term-missing


## 4. CI
Workflow GitHub Actions pour exécuter les tests et publier le rapport de couverture.

## 5. Sécurité
API key simple via `x-api-key`.manager.

