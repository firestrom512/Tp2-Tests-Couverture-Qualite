"""Partie B2 : tests d'intégration HTTP avec Flask test_client."""

import pytest


def test_simulate_should_return_breakdown_and_200(client, order_body):
    response = client.post("/orders/simulate", json=order_body)
    assert response.status_code == 200
    assert response.json == {"subtotal": 25, "discount": 0, "deliveryFee": 3, "surge": 1, "total": 28}


def test_simulate_should_apply_valid_promo(client, order_body):
    order_body["promoCode"] = "BIENVENUE20"
    response = client.post("/orders/simulate", json=order_body)
    assert response.status_code == 200
    assert response.json["discount"] == 5
    assert response.json["total"] == 23


def test_simulate_should_reject_expired_promo(client, order_body):
    order_body["promoCode"] = "EXPIRE"
    response = client.post("/orders/simulate", json=order_body)
    assert response.status_code == 400
    assert "expiré" in response.json["error"]


def test_simulate_should_reject_empty_cart(client, order_body):
    order_body["items"] = []
    assert client.post("/orders/simulate", json=order_body).status_code == 400


def test_simulate_should_reject_outside_zone(client, order_body):
    order_body["distance"] = 11
    assert client.post("/orders/simulate", json=order_body).status_code == 400


def test_simulate_should_reject_closed_hours(client, order_body):
    order_body["hour"] = 23
    assert client.post("/orders/simulate", json=order_body).status_code == 400


def test_simulate_should_apply_surge_on_friday(client, order_body):
    order_body.update({"hour": 20, "dayOfWeek": "friday"})
    response = client.post("/orders/simulate", json=order_body)
    assert response.status_code == 200
    assert response.json["deliveryFee"] == 5.4
    assert response.json["total"] == 30.4


def test_simulate_should_reject_missing_body(client):
    assert client.post("/orders/simulate").status_code == 400


def test_simulate_should_reject_missing_required_field(client):
    assert client.post("/orders/simulate", json={"items": []}).status_code == 400


def test_simulate_should_reject_unknown_promo(client, order_body):
    order_body["promoCode"] = "UNKNOWN"
    response = client.post("/orders/simulate", json=order_body)
    assert response.status_code == 404


def test_orders_should_save_order_and_return_201(client, order_body):
    response = client.post("/orders", json=order_body)
    assert response.status_code == 201
    assert response.json["id"] == 1
    assert response.json["total"] == 28


def test_orders_should_be_retrievable_by_id(client, order_body):
    created = client.post("/orders", json=order_body).json
    fetched = client.get(f"/orders/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json == created


def test_orders_should_assign_distinct_ids(client, order_body):
    one = client.post("/orders", json=order_body).json
    two = client.post("/orders", json=order_body).json
    assert one["id"] != two["id"]


def test_orders_should_reject_invalid_order(client, order_body):
    order_body["distance"] = -1
    assert client.post("/orders", json=order_body).status_code == 400


def test_orders_should_not_save_invalid_order(client, order_body):
    order_body["distance"] = 20
    assert client.post("/orders", json=order_body).status_code == 400
    assert client.get("/orders/1").status_code == 404


def test_orders_should_not_consume_id_for_invalid_order(client, order_body):
    order_body["items"] = []
    client.post("/orders", json=order_body)
    order_body["items"] = [{"name": "Pizza", "price": 12.5, "quantity": 2}]
    assert client.post("/orders", json=order_body).json["id"] == 1


def test_get_order_should_return_404_when_missing(client):
    response = client.get("/orders/999")
    assert response.status_code == 404
    assert "error" in response.json


def test_get_order_should_return_complete_structure(client, order_body):
    client.post("/orders", json=order_body)
    response = client.get("/orders/1")
    assert response.status_code == 200
    assert {"id", "subtotal", "discount", "deliveryFee", "surge", "total", "items"} <= response.json.keys()


def test_get_order_should_404_for_invalid_route(client):
    assert client.get("/orders/abc").status_code == 404


def test_promo_validate_should_accept_valid_code(client):
    response = client.post("/promo/validate", json={"promoCode": "BIENVENUE20", "subtotal": 50})
    assert response.status_code == 200
    assert response.json == {"valid": True, "subtotal": 50, "discount": 10, "finalTotal": 40}


def test_promo_validate_should_reject_expired_code(client):
    response = client.post("/promo/validate", json={"promoCode": "EXPIRE", "subtotal": 50})
    assert response.status_code == 400
    assert "expiré" in response.json["error"]


def test_promo_validate_should_reject_below_minimum(client):
    response = client.post("/promo/validate", json={"promoCode": "BIENVENUE20", "subtotal": 10})
    assert response.status_code == 400
    assert "minimum" in response.json["error"]


def test_promo_validate_should_404_for_unknown_code(client):
    response = client.post("/promo/validate", json={"promoCode": "UNKNOWN", "subtotal": 50})
    assert response.status_code == 404
    assert "inconnu" in response.json["error"]


def test_promo_validate_should_reject_missing_promo_code(client):
    assert client.post("/promo/validate", json={"subtotal": 50}).status_code == 400


@pytest.mark.parametrize("body", [None, {}, {"promoCode": "BIENVENUE20"},
                                   {"promoCode": "BIENVENUE20", "subtotal": -1}])
def test_promo_validate_should_reject_invalid_payload(client, body):
    response = client.post("/promo/validate", json=body) if body is not None else client.post("/promo/validate")
    assert response.status_code == 400


def test_app_should_reset_orders_for_new_test(client, app, order_body):
    client.post("/orders", json=order_body)
    assert client.get("/orders/1").status_code == 200
    from src.app import reset_orders

    reset_orders(app)
    assert client.get("/orders/1").status_code == 404
    assert client.post("/orders", json=order_body).json["id"] == 1
