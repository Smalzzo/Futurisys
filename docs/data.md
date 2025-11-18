# Données

## Sources

Les données proviennent de la fusion de **trois sources principales** :

- **SIRH**  
  - Informations RH de base : âge, genre, département, poste, distance domicile–travail, ancienneté, etc.
  - Identifiant clé : `id`.

- **Évaluations annuelles**  
  - Résultats d’évaluation individuelle : `note_evaluation`, nombre d’expériences, participation à des actions, etc.
  - Identifiant clé : `id`.

- **Sondage annuel**  
  - Perception et satisfaction des employés :  
    - `satisfaction_employee`  
    - `satisfaction_employee_equilibre_pro`  
    - `satisfaction_employee_nature`  
    - autres scores de satisfaction / engagement.
  - Identifiant clé : `id`.

Les trois tables sont jointes sur `id` (converti en chaîne de caractères) pour obtenir un **jeu de données intégré**.

---

## Dictionnaire de variables

### Variable cible

- `a_quitte_l_entreprise`  
  - Type : binaire (`OUI` / `NON`, ensuite converti en booléen).  
  - Rôle : cible du modèle (1 si l’employé a quitté l’entreprise).

---

### Variables explicatives nominales (non ordonnées)

Variables catégorielles sans ordre naturel, encodées avec un **OneHotEncoder** dans le pipeline :

- `departement` : département d’affectation.
- `poste` : intitulé / famille de poste.
- `domaine_etude` : domaine d’étude initial (ex. INFORMATIQUE, FINANCE...).
- `genre` : genre de l’employé.
- `statut_marital` : ex. CÉLIBATAIRE, MARIÉ(E)… (souvent binarisé dans le notebook).
- `heure_supplementaires` : indicateur de recours aux heures supplémentaires (OUI/NON → booléen).
- `poste_x_statut` : feature dérivée combinant poste et statut marital (interaction).

👉 Ces colonnes sont regroupées dans une liste de colonnes **nominales** dans le notebook et passées au préprocesseur.

---

### Variables explicatives ordinales (ordonnées)

Variables catégorielles **ordonnées**, encodées via un **OrdinalEncoder** avec un ordre explicite des modalités :

- `frequence_deplacement` : fréquence de déplacement (par ex. JAMAIS < PARFOIS < SOUVENT).  
- `revenu_mensuel_pallier` : paliers de revenu mensuel.  
- `anciennete_pallier` : paliers d’ancienneté dans l’entreprise.  
- `exp_totale_pallier` : paliers d’expérience totale.  
- `satisfaction_globale_pallier` : paliers de satisfaction globale.  
- Potentiellement d’autres `*_pallier` définis dans le notebook.

👉 L’ordre exact des modalités est défini dans un dictionnaire `ORDINAL_CATS` dans le notebook pour éviter tout encodage incohérent.

---

### Variables numériques

Les variables numériques correspondent aux colonnes de `X` qui ne sont ni nominales ni ordinales.  
Parmi les plus importantes (d’après l’analyse d’importance des features) :

- `age` : âge de l’employé.  
- `distance_domicile` : distance domicile–travail.  
- `nombre_experiences` : nombre d’expériences professionnelles.  
- `nombre_participation` : nombre de participations à certaines actions (formations, projets, etc.).  
- `note_evaluation` : note d’évaluation annuelle.  
- `niveau_hierarchique` : niveau de responsabilité dans l’organisation.  
- `annee_experience_totale` : nombre d’années d’expérience totale.  
- `heure_supplementaires` (si codée directement en 0/1).  

Scores de satisfaction issus du sondage (souvent numériques ou transformés) :

- `satisfaction_employee`  
- `satisfaction_employee_equilibre_pro`  
- `satisfaction_employee_nature`

👉 Ces colonnes sont utilisées telles quelles dans le bloc **numérique** du préprocesseur (imputation + éventuellement mise à l’échelle/log-transform).

---

### Variables dérivées / transformations

Plusieurs transformations sont appliquées dans le notebook avant ou dans le pipeline ML :

- Conversion systématique des colonnes `object` en **majuscules** et suppression des espaces superflus.
- Conversion de colonnes texte en booléen (ex. `"OUI" → True`, `"NON" → False`).
- Création de paliers (`*_pallier`) pour :
  - revenu mensuel  
  - ancienneté  
  - expérience totale  
  - satisfaction
- Création de features d’interaction (ex. `poste_x_statut`).
- Colonnes `*_log` pour certaines variables continues (log-transform) afin de réduire l’influence des valeurs extrêmes.

---

## Qualité et préparation

Les principales étapes de préparation sont :

- **Nettoyage des identifiants**
  - Conversion de `id` en chaîne (`astype(str)`) pour éviter les incohérences `int` vs `str`.
  - Jointures internes (`how="inner"`) pour ne garder que les employés présents dans toutes les sources.

- **Traitement des valeurs manquantes**
  - Imputation numérique (ex. médiane) pour les colonnes continues.
  - Imputation catégorielle (ex. modalité la plus fréquente ou catégorie spéciale) pour les colonnes nominales/ordinales.
  - Suppression éventuelle de lignes trop incomplètes (cf. notebook).

- **Valeurs aberrantes**
  - Analyse via `scipy.stats.zscore` et visualisations.
  - Possibilité de **capper** certaines variables (winsorisation) ou de les transformer (log).

- **Filtrage**
  - Exclusion de lignes incohérentes (dates impossibles, âges extrêmes selon règles métier, etc.).
  - Filtrage éventuel sur des statuts non pertinents (ex. stagiaires, alternants, selon le périmètre métier retenu).

L’ensemble de ces règles est codé dans le notebook de préparation des données et doit être **conservé** pour garantir la reproductibilité du modèle.
