"""Configuration des fixtures de tests HTTP indépendants."""

from datetime import date

import pytest

from src.app import create_app, reset_orders


@pytest.fixture
def app():
    flask_app = create_app(today_provider=lambda: date(2026, 11, 21))
    flask_app.config["TESTING"] = True
    reset_orders(flask_app)
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def order_body():
    return {"items": [{"name": "Pizza", "price": 12.5, "quantity": 2}],
            "distance": 5, "weight": 2, "hour": 15, "dayOfWeek": "tuesday"}
