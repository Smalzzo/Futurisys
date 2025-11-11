# Modèle de Machine Learning

## Vue d’ensemble
- Format: `joblib`/`pkl` (pipeline scikit-learn)
- Fichier: `app/ml/model.pkl` (configurable via `MODEL_PATH`)

## Performances (à compléter)
- Jeu de données: …
- Métriques: AUC, précision, rappel, F1
- Courbes: ROC/PR (liens ou images)

## Données d’entrée attendues
- Voir `docs/api.md` et `app/api/schemas.py` pour la liste complète des features.
- Normalisations appliquées côté API (`_normalize_payload`).

## Chargement et inférence
- Service: `app/ml/serve.py` → `ModelService`
- Méthodes:
  - `predict_proba(payload: dict) -> float`
  - `predict_label(payload: dict) -> int`

## Maintenance du modèle
- Versionner le modèle (nom de fichier avec version: `model-YYYYMMDD.pkl`)
- Historiser métriques et jeux de validation
- Procédure de mise à jour:
  1. Entraîner et valider
  2. Enregistrer `model.pkl` et publier (Hub ou LFS)
  3. Déployer (Docker/Space) et vérifier `health` + tests de fumée

