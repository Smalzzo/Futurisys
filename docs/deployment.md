# Déploiement

## Docker local
```
docker build -t ml-service .
docker run -p 7860:7860 --env-file .env ml-service
```

## Hugging Face Spaces (Docker)
- `Dockerfile` expose l’app sur port 7860 (uvicorn)
- Définir les variables d’env dans Settings > Variables (API_KEY, MODEL_PATH, …)
- Option: héberger `model.pkl` via Git LFS ou Hugging Face Hub

## GitHub Actions
- Workflow CI: `.github/workflows/ci.yml` (build + tests + coverage)
- Option: ajouter un job de publication PyPI ou un déploiement de la doc (voir plus bas)

