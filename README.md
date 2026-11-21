# TP2 — Tests, Couverture & Qualité

Travail complet en Python (Flask + pytest + pytest-cov + Ruff) : exercices de découverte (A1–A4), exercices supplémentaires (A5–A7), moteur de tarification (B1), API et tests d'intégration (B2), couverture ≥ 80 % (B3), qualité du code (B4) et GitHub Actions (C1).

## Installation (Windows PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
ruff check .
pytest
python run.py
```

L'API écoute sur `http://127.0.0.1:5000`. Les tests HTTP n'ont pas besoin de lancer le serveur.

## Commandes

- `pytest` : tests et couverture (échec automatique sous 80 %).
- `pytest --cov-report=html` : rapport HTML dans `htmlcov/index.html`.
- `ruff check .` : linter.

## Endpoints

| Méthode | URL | Succès | Description |
| --- | --- | --- | --- |
| POST | `/orders/simulate` | 200 | Simuler le prix sans stockage |
| POST | `/orders` | 201 | Enregistrer une commande avec ID |
| GET | `/orders/1` | 200 ou 404 | Consulter une commande |
| POST | `/promo/validate` | 200, 400 ou 404 | Valider une réduction |

Exemple avec PowerShell :

```powershell
$body = @{items=@(@{name='Pizza';price=12.5;quantity=2});distance=5;weight=2;hour=15;dayOfWeek='tuesday'} | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/orders/simulate -ContentType 'application/json' -Body $body
```

Exemple de résultat :

```json
{"subtotal":25.0,"discount":0.0,"deliveryFee":3.0,"surge":1.0,"total":28.0}
```

Codes de démonstration : `BIENVENUE20` (-20 % dès 15 €), `FIXE5` (-5 € dès 10 €), `EXPIRE` (volontairement expiré), `CADEAU100` (-100 %), `GROSSE10` (-10 €). Les codes valides ont une expiration future fixée au 31/12/2099 pour garantir les tests.

### Choix explicités pour les zones ambiguës de l'énoncé

- Distance = 0 km : accepté. Distance > 10 km : erreur 400. Quantité = 0 : erreur 400.
- À 22:00, service encore ouvert ; après 22:00, fermé. Sur les créneaux non précisés entre 10:00 et 22:00, tarif normal 1.0.
- `deliveryFee` est le prix de livraison après application du surge ; le surge ne touche pas le sous-total des articles.
- L'offre bonus `buyXgetY` déduit les articles offerts sur la base du prix unitaire et du total courant.
- Le paiement et le stockage sont simulés : pas de base de données, commandes réinitialisées à chaque démarrage.
- La date d'expiration des promos utilise une horloge injectable en tests ; le calcul des heures de pointe ne lit **jamais** l'heure système.

## Documentation de la méthode TDD

Voir [docs/EXPERIMENTS.md](docs/EXPERIMENTS.md) pour les manipulations A3 et l'ordre Red → Green → Refactor d'A4.

## Structure

```text
src/               utils.py, validators.py, pricing.py, app.py
run.py             démarre le serveur sans gêner les tests
tests/             tests unitaires et HTTP
.github/workflows/ci.yml
pyproject.toml     Ruff + pytest + seuil de couverture
```
