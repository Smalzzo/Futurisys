# Maintenance

## Protocole de mise à jour du modèle
1. Entraîner et évaluer (journaliser les métriques)
2. Versionner et publier `model.pkl` (Hub ou LFS)
3. Mettre à jour la variable `MODEL_PATH` ou les variables Hub
4. Redéployer (Docker/Space)

## Mises à jour régulières
- Planifier une réentraînement (mensuel/trimestriel)
- Surveiller la dérive de données et de performance

## Tests de régression
- Jeux de tests figés + appels API de fumée

