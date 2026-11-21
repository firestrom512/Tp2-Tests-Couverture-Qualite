# A3 — Analyse des tests en échec et A4 — TDD

## A3 : expériences reproductibles (ne pas laisser les bugs dans `main`)

1. `calculateAverage([10,12,14])` retourne normalement `12`. Remplacer la division `/` par `*` dans la moyenne fait recevoir `108` au lieu de `12` (pour la variante `sum(numbers) * len(numbers)`). Le test de moyenne échoue.
2. Enlever le contrôle `@` dans `isValidEmail` laisse passer les adresses invalides si le validateur devient trop permissif. Les tests négatifs (notamment `invalid`, `@domain.com`, `user@`) doivent alors détecter le problème. Le nombre exact dépend de la modification introduite.
3. Enlever `.lower()` de la partie après la première lettre de `capitalize` permet encore `hello -> Hello`, mais casse `WORLD -> World`.
4. Revenir au code correct et relancer `pytest` (tout doit être vert).

## A4 : étapes Red → Green → Refactor

Pour `sortStudents(students, sortBy, order='asc')` :

1. **RED** : écrire et exécuter `test_sort_grade_ascending` avant la fonction (échec attendu).
2. **GREEN** : implémenter le tri par `grade`, jusqu'à obtenir un test vert.
3. **REFACTOR** : factoriser `sorted(..., key=...)` puis ajouter les tests, un par un : `grade desc`, `name asc`, `age asc`, `null`, `[]`, immutabilité, ordre par défaut.
4. **GREEN final** : exécuter toute la suite.

Ces instructions décrivent la procédure pédagogique ; le résultat final conserve le code correct et les tests.
