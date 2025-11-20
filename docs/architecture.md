# Architecture de l’API Futurisys

Cette page décrit les composants techniques du service et la façon dont ils coopèrent pour délivrer une prédiction fiable.

---

## Vue d’ensemble

1. **FastAPI** instancie l’application (`app/main.py`) et expose les routes sous `/api/v1`.
2. **ModelService** (`app/ml/serve.py`) charge le pipeline scikit-learn sérialisé dans `model.pkl` et applique le seuil F2 optimisé.
3. **Base de données** SQLite/PostgreSQL stocke les features (`EmployeeFeatures`) ainsi que les journaux (`PredictionLog`).
4. **Couche d’authentification** (`app/api/deps.py`) protège les routes via la clé API.

---

## Composants principaux

- **FastAPI / Lifespan** (`app/main.py`)
  - Crée l’application, prépare le dossier `./data`, initialise la base SQLite si besoin et précharge le modèle.
  - Route racine `/` et route de santé `/api/v1/health`.

- **Routes API** (`app/api/predict.py`, `app/api/logs.py`)
  - `POST /predict` et `GET /predict/by-id/{employee_id}` orchestrent la validation Pydantic, la normalisation des features et l’appel du modèle.
  - `GET /logs/prediction/{employee_id}` relit les journaux.

- **Service ML** (`app/ml/serve.py`, `app/ml/model_loader.py`)
  - Charge le pipeline via joblib, fournit `predict_label` / `predict_proba`, applique le seuil optimal issu de l’entraînement.

- **Dépendances et sécurité** (`app/api/deps.py`)
  - Vérifie la présence et la valeur de l’en-tête `x-api-key`.

- **Base de données** (`app/db/*`)
  - SQLAlchemy + moteur (SQLite par défaut, PostgreSQL si `DATABASE_URL` défini).
  - `EmployeeFeatures` : toutes les colonnes utilisées par le modèle.
  - `PredictionLog` : persistance des requêtes (payloads, latences, sorties).

- **Configuration** (`app/core/config.py`)
  - Centralise les variables (`API_KEY`, `DATABASE_URL`, `POSTGRES_*`, `model_path`, etc.) et construit l’URL SQLAlchemy.

---

## Flux de données

1. Le client authentifié envoie un JSON à `/api/v1/predict`.
2. Pydantic (`PredictIn`) nettoie/valide les champs, puis `_normalize_payload` complète les colonnes attendues.
3. `ModelService` calcule la probabilité puis applique le seuil → réponse `OUI/NON`.
4. La requête est journalisée (`save_prediction_log`) avec latence, payload normalisé et sortie.
5. Via `/predict/by-id/{employee_id}`, les features proviennent de la base (`EmployeeFeatures`) au lieu du payload direct.

---

## Schéma d’architecture

```mermaid
flowchart LR
    Client -->|HTTP + JSON + x-api-key| API[FastAPI /api/v1]
    API --> Dep[get_api_key()]
    API --> Val[Pydantic PredictIn]
    Val --> Norm[_normalize_payload]
    Norm --> ML[ModelService (model.pkl)]
    ML --> Resp[Réponse JSON]

    API --> DB[(SQLite / PostgreSQL)]
    API --> Logs[PredictionLog]
    Logs --> DB
```
