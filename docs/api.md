# API de prédiction Futurisys

Service FastAPI exposant le modèle de Machine Learning qui estime la probabilité qu’un employé quitte l’entreprise.

- Framework : **FastAPI**
- Préfixe global : `/api/v1`
- Authentification : **clé API** dans l’en‑tête `x-api-key`
- Formats : requêtes et réponses **JSON UTF‑8**

---

## Authentification

Toutes les routes (hors `/health`) exigent la clé API configurée côté serveur (`API_KEY`).

```http
x-api-key: <VOTRE_CLE_API>
```

- En cas de clé absente ou incorrecte, FastAPI retourne `401 Unauthorized`.
- Pensez à stocker la clé dans un `.env` et à la passer via `--env-file` ou via les variables d’environnement de votre orchestrateur.

---

## Résumé des endpoints

| Méthode | Route | Description | Authentification |
| --- | --- | --- | --- |
| `GET` | `/api/v1/health` | Vérifie que l’API répond | Non |
| `POST` | `/api/v1/predict` | Inférence à partir d’un payload JSON | Oui (`x-api-key`) |
| `GET` | `/api/v1/predict/by-id/{employee_id}` | Inférence en relisant les features stockées en base | Oui (`x-api-key`) |
| `GET` | `/api/v1/logs/prediction/{employee_id}` | Dernière prédiction enregistrée pour un employé | Oui (`x-api-key`) |

---

## POST `/api/v1/predict`

### Payload attendu

Corps JSON validé par `PredictIn` (`app/api/schemas.py`). Seul `id_employee` est obligatoire ; les autres champs sont optionnels mais fortement recommandés pour obtenir une prédiction fiable.

Extrait des champs disponibles :

- **Identité** : `id_employee` (entier strict).
- **Numériques** : `age`, `nombre_experiences_precedentes`, `annees_dans_le_poste_actuel`, `note_evaluation_actuelle`, `distance_domicile_travail`, `annees_dans_l_entreprise`, `annee_experience_totale`, etc.
- **Catégorielles** : `genre`, `statut_marital`, `departement`, `poste`, `heure_supplementaires`, `domaine_etude`.
- **Ordinales** : `frequence_deplacement`.

Les chaînes sont automatiquement normalisées (suppression des espaces, uppercase, YES/NO → OUI/NON). Les champs numériques sont rejetés s’ils sont négatifs.

### Exemple

```http
POST /api/v1/predict HTTP/1.1
Host: localhost:8000
x-api-key: change-me
Content-Type: application/json

{
  "id_employee": 101,
  "age": 36,
  "departement": "Tech",
  "poste": "DEVELOPPEUR",
  "heure_supplementaires": "oui",
  "annees_dans_l_entreprise": 4,
  "annee_experience_totale": 9,
  "note_evaluation_actuelle": 3.8,
  "frequence_deplacement": "Parfois"
}
```

### Réponse

```json
{
  "employee_id": 101,
  "pred_quitte_entreprise": "NON"
}
```

- `200 OK` si l’inférence s’est bien passée.
- `422 Unprocessable Entity` lorsque le schéma Pydantic refuse la requête (champ manquant, type incorrect, valeur hors domaine).
- `500 Internal Server Error` si le modèle ou la base rencontrent une erreur (voir les logs applicatifs).

Chaque appel journalise la requête via `PredictionLog` avec la latence.

---

## GET `/api/v1/predict/by-id/{employee_id}`

Effectue une prédiction en relisant les features déjà présentes en base (table `EmployeeFeatures`). Le paramètre `employee_id` doit être un entier ≥ 1.

```http
GET /api/v1/predict/by-id/101
x-api-key: change-me
```

Réponse :

```json
{
  "employee_id": 101,
  "pred_quitte_entreprise": "OUI"
}
```

- `422` est retourné si aucun enregistrement n’est trouvé pour cet identifiant.
- Le payload utilisé et la réponse sont journalisés de la même manière que `/predict`.

---

## GET `/api/v1/logs/prediction/{employee_id}`

Expose le dernier log de prédiction enregistré pour un employé via `PredictionLog`.

```json
{
  "employee_id": 101,
  "payload": {
    "employee_id": 101,
    "features": {
      "age": 36,
      "poste": "DEVELOPPEUR",
      "frequence_deplacement": "PARFOIS",
      "...": "..."
    }
  },
  "pred_quitte_entreprise": "NON"
}
```

- `404 Not Found` si aucun log n’existe encore pour cet `employee_id`.

---

## GET `/api/v1/health`

Endpoint léger qui retourne simplement :

```json
{ "status Api": "ok" }
```

Utile pour des probes ou tests de connectivité. Aucun header d’authentification n’est requis.
