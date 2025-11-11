# API

- Base URL: `/api/v1`
- Auth: en-tête `x-api-key: <votre-cle>`

## Endpoints

### Santé
- `GET /api/v1/health`
- Réponse: `{ "status Api": "ok" }`

### Prédiction directe
- `POST /api/v1/predict`
- Headers: `x-api-key`
- Corps JSON minimal (exemple):
```
{
  "age": 35,
  "poste": "Dev"
}
```
- Réponse:
```
{
  "employee_id": null,
  "pred_quitte_entreprise": "OUI" | "NON"
}
```

Exemple curl:
```
curl -H "x-api-key: change" \
     -H "Content-Type: application/json" \
     -X POST http://localhost:8000/api/v1/predict \
     -d '{"age": 35, "poste": "Dev"}'
```

### Prédiction par identifiant
- `GET /api/v1/predict/by-id/{employee_id}`
- Headers: `x-api-key`
- Réponse:
```
{
  "employee_id": 123,
  "pred_quitte_entreprise": "OUI" | "NON"
}
```

Note: les schémas d’entrée sont définis dans `app/api/schemas.py`.

