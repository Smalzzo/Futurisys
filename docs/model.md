# Modèle de Machine Learning

## Vue d’ensemble
- Format: `joblib`/`pkl` (pipeline scikit-learn)
- Fichier: `app/ml/model.pkl` (configurable via `MODEL_PATH`)
- Modèles évalués : **LogisticRegression**, **RandomForestClassifier**, **GradientBoostingClassifier**
- Prétraitement: `ColumnTransformer` (numériques/catégorielles, imputation + encodage)

## Données (résumé)
- Cible: `a_quitte_l_entreprise` (binaire 0/1)
- Déséquilibre: **présent** → géré via `class_weight="balanced"` pour la régression logistique (et réglages adaptés pour les autres)
- Split: train/validation/test + validation croisée (k-fold) **sans fuite de données** (transfos dans pipeline)

> Détails complets dans `docs/data.md` et `docs/evaluation.md`.

## Métriques
- **ROC AUC** et **Average Precision (PR AUC)** rapportées sur validation/test
- **Seuil décisionnel** optimisé pour **F2** (β=2) à partir de la courbe PR  
  **Seuil retenu:** `0.12593` (variable `SEUIL_FIXE` dans le code)
- **Confusion matrix** et **classification report** fournis au seuil F2


> Insérer ici *les valeurs numériques* finales (ROC AUC, AP, F2 @ seuil, précision/recall, etc.) et, si possible, des captures des courbes ROC/PR.



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
  - `predict_proba(payload: dict) -> float` (proba classe positive)
  - `predict_label(payload: dict, seuil: float=SEUIL_FIXE) -> int`

## Maintenance du modèle
- Versionner le modèle (nom de fichier avec version: `model-YYYYMMDD.pkl`)
- Historiser métriques et jeux de validation
- Procédure de mise à jour:
  1. Entraîner et valider
  2. Enregistrer `model.pkl` et publier (Hub)
  3. Déployer (Docker/Space) et vérifier `health` + tests de fumée

