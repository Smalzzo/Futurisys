# Évaluation

## Méthodologie
- Split train/test (avec stratification)
- **Validation croisée k-fold** sur le train (toutes les steps dans Pipeline pour éviter la fuite)
- Optimisation du **seuil F2** sur validation via `precision_recall_curve` → choix du seuil `0.12593`

## Métriques
- **F2 @ 0.12593**: <0.63> (avec précision 0.33/recall 0.81)
- **Confusion matrix @ 0.12593**: <TN, FP, FN, TP à compléter>

## Courbes
-![F2/recall/precision](image.png)

![Matrice de confusion](image-1.png)

## Analyse d’erreurs
On cherche ici à maximiser le rappel pour minimiser les faux negatifs
