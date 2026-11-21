"""Lancer l'API (séparé de la configuration pour les tests)."""

from src.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=False)
