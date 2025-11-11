# Démarrage

## Lancer en local
```
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- Docs interactives: http://localhost:8000/docs
- Prefix API: `/api/v1`

## Variables d’environnement
- `API_KEY`: clé API attendue (en-tête `x-api-key`)
- `DATABASE_URL`: URL SQLAlchemy (par défaut SQLite)
- `MODEL_PATH`: chemin vers `model.pkl` (défaut: `app/ml/model.pkl`)
- Hugging Face Hub (optionnel): `MODEL_REPO_ID`, `MODEL_FILENAME`, `HF_TOKEN`

## Exemple rapide
```
curl -H "x-api-key: change" \
     -H "Content-Type: application/json" \
     -X POST http://localhost:8000/api/v1/predict \
     -d '{"age": 35, "poste": "Dev"}'
```
