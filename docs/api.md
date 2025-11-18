# API de prédiction Futurisys

Cette API expose un modèle de Machine Learning qui prédit si un employé est susceptible de **quitter l’entreprise**.

- Framework : **FastAPI**
- Préfixe des routes : `/api/v1`
- Format : JSON
- Authentification : **clé API** via l’en-tête HTTP `x-api-key`

---

## 1. Authentification par API Key

Toutes les routes de prédiction sont protégées.

### En-tête attendu

```http
x-api-key: <VOTRE_CLE_API>
