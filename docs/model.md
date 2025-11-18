# Modèle de Machine Learning

## Vue d’ensemble
- Format: `joblib`/`pkl` (pipeline scikit-learn)
- Fichier: `app/ml/model.pkl` (configurable via `MODEL_PATH`)
- Modèles évalués : **LogisticRegression**, **RandomForestClassifier**, **GradientBoostingClassifier**
- Prétraitement: `ColumnTransformer` (numériques/catégorielles, imputation + encodage)

# Modèle ML

## Objectif

Prédire la probabilité qu’un employé **quitte l’entreprise** (démission) à partir :

- de caractéristiques RH (âge, poste, département, ancienneté…),
- de résultats d’évaluation,
- et de réponses à un sondage annuel de satisfaction.

La variable cible est :

- `a_quitte_l_entreprise` (binaire : 1 si l’employé a quitté l’entreprise, 0 sinon).

---

## Pipeline de modélisation

Le modèle est encapsulé dans un **pipeline scikit-learn** :

1. **Prétraitement (`prep`)**
   - Encodage **OneHotEncoder** pour les variables nominales :
     - `departement`, `poste`, `domaine_etude`, `genre`,
       `statut_marital`, `heure_supplementaires`, `poste_x_statut`, etc.
   - Encodage **OrdinalEncoder** pour les variables ordinales :
     - `frequence_deplacement`, `revenu_mensuel_pallier`,
       `anciennete_pallier`, `exp_totale_pallier`,
       `satisfaction_globale_pallier`, etc.  
     → ordres des modalités définis explicitement dans un dictionnaire.
   - Colonnes numériques :
     - imputation des valeurs manquantes,
     - transformations éventuelles (`*_log`) pour certaines variables continues.

2. **Estimateur (`modele`)**
   - Modèle retenu : **GradientBoostingClassifier**
   - Paramètres : issus d’un tuning simple (ou paramètres par défaut), ensuite optimisés via validation croisée + recherche de seuil.

Le tout est sérialisé dans un fichier unique `model.pkl` utilisé à l’inférence.

---

## Comparaison de modèles

Plusieurs modèles ont été testés avec une **validation croisée** et optimisation du **F2** :

- **LogisticRegression**
- **RandomForestClassifier**
- **GradientBoostingClassifier** (modèle final)

Avec seuil optimisé :

- Le **GradientBoostingClassifier** obtient un F2 moyen ≈ **0.65**, avec un **rappel ≈ 0.79**.
- La Logistic Regression est légèrement en dessous (F2 ≈ 0.64).
- Le RandomForest est encore un peu plus bas (F2 ≈ 0.60).

Compte tenu de l’objectif métier (maximiser le rappel), le GradientBoosting a été choisi.

---

## Choix du seuil de classification

Plutôt que d’utiliser le seuil standard `0.5`, un **seuil optimal** est appris pour **maximiser F2** :

- Seuil retenu : **0.12593**  
- Méthode :
  - utilisation de `precision_recall_curve`,
  - calcul de F2 pour chaque seuil candidat,
  - choix du seuil maximisant F2 sur la validation.

Effet sur les erreurs :

- **Seuil 0.5** → FN ≈ 31 (beaucoup de départs ratés).
- **Seuil 0.12593** → FN ≈ 8 (FN divisés par ~4).

Le modèle est donc **plus sensible** (plus de positifs prédits) mais laisse passer beaucoup moins de cas à risque.

---

## Principales variables explicatives

D’après les analyses d’importance (feature importance) du GradientBoosting :

- `heure_supplementaires`
- `age`
- `nombre_participation`
- `satisfaction_employee`
- `nombre_experiences`
- `poste`
- `annee_experience_totale`
- `departement`
- `frequence_deplacement`
- `satisfaction_employee_equilibre_pro`
- `distance_domicile`
- `note_evaluation`
- `niveau_hierarchique`
- `satisfaction_employee_nature`

Interprétation qualitative :

- Les **heures supplémentaires**, la **satisfaction** (globale et sur plusieurs dimensions) et la **situation professionnelle** (poste, niveau hiérarchique, expérience) jouent un rôle majeur.
- Les variables de **confort** (distance domicile, équilibre vie pro/perso) contribuent également au risque de départ.

---

## Reproductibilité

Pour reproduire le modèle :

1. Reprendre le notebook d’entraînement.
2. Appliquer exactement les mêmes étapes de préparation des données.
3. Réentraîner le pipeline (préprocesseur + GradientBoostingClassifier).
4. Réapprendre un seuil optimal F2.
5. Sérialiser le pipeline complet dans `model.pkl`.

⚠️ Toute modification de la structure de données (nouvelles colonnes, changement de modalités…) nécessite :
- une mise à jour du préprocesseur,
- une ré-évaluation du modèle,
- et idéalement une nouvelle version (modèle + documentation).


