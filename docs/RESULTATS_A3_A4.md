# A3 / A4 — Résultats des expériences réellement exécutées

Ces essais ont été réalisés avec pytest sur des **copies temporaires** des sources. Aucun bug volontaire n'est conservé dans `main`.

## A3 — Bugs volontaires

1. Dans `calculateAverage`, remplacement de `sum(numbers) / len(numbers)` par `sum(numbers) * len(numbers)`. Résultat : **4 tests échoués, 3 réussis**. Exemple : `[10,12,14]` attend **12**, reçoit **108**.
2. Dans `isValidEmail`, le symbole `@` a été rendu facultatif dans l'expression régulière. Résultat : **2 tests échoués, 10 réussis**. Les adresses `userdomain.com` et `name.surname.com` sont acceptées à tort.
3. Dans `capitalize`, suppression du `.lower()` sur la suite de la chaîne. Résultat : **2 tests échoués, 4 réussis**. Exemples : `WORLD` est reçu au lieu de `World` et `MIxEd` au lieu de `Mixed`.

Les modifications ont ensuite été annulées.

## A4 — Red → Green sur le tri

- **RED :** `sortStudents` renvoie provisoirement `[]`. Pour le tri des notes, le test attend `[8,12,18]`, mais reçoit `[]` : **1 test échoué**.
- **GREEN :** restauration de l'implémentation correcte `sorted(..., key=...)` : **1 test réussi**.
- **REFACTOR / suite :** les autres scénarios sont couverts par `tests/test_utils.py` : tri croissant/décroissant, nom, âge, entrées nulles/vides, immutabilité et valeur par défaut.

Cette démonstration documente le comportement du TDD. Le pipeline final exécute ensuite la suite complète sur GitHub Actions.
