
---

## 2️⃣ `architecture.md`

```markdown
# Architecture de l’API Futurisys

Cette page décrit les composants techniques du service Futurisys et la façon dont ils interagissent.

---

## 1. Composants principaux

- **FastAPI** (`app/main.py`)
  - Création de l’application
  - Cycle de vie (`lifespan`)
  - Route racine `/`
  - Inclusion des routes API via `app.api.router`

- **API & routes** (`app/api/predict.py`)
  - `POST /predict`
  - `GET /predict/by-id/{employee_id}`
  - `GET /health`

- **Service ML** (`app/ml/serve.py`)
  - Classe `ModelService`
  - Chargement du pipeline scikit-learn (`model.pkl`)
  - `predict_proba()` / `predict_label()` avec seuil F2 optimisé

- **Dépendances API** (`app/api/deps.py`)
  - Vérification de la clé API (`get_api_key`)

- **Base de données** (`app/db/session.py`, `app/db/models.py`, `app/db/repository.py`, `app/db/base.py`)
  - ORM SQLAlchemy
  - `EmployeeFeatures` : features d’employés
  - `PredictionLog` : logs de prédiction
  - `ErrorLog` : logs d’erreur (si utilisé)

- **Configuration** (`app/core/config.py`)
  - Classe `Settings`
  - Sélection automatique du backend : SQLite (défaut) ou autre via `DATABASE_URL`.

---

## 2. Schéma d’architecture

```mermaid
flowchart LR
    Client -->|HTTP + JSON + x-api-key| API[FastAPI /api/v1]
    API --> Dep[get_api_key()]
    API --> Val[Pydantic PredictIn]
    Val --> Norm[_normalize_payload + features dérivées]
    Norm --> ML[ModelService (model.pkl)]
    ML --> Resp[Réponse JSON]

    API --> DB[(SQLite / PostgreSQL)]
    API --> Logs[PredictionLog]
    Logs --> DB
