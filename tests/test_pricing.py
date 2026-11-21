"""Partie B1 : moteur de tarification et tests unitaires."""

from datetime import date

import pytest

from src.pricing import (
    PROMO_CODES,
    applyPromoCode,
    calculateDeliveryFee,
    calculateOrderTotal,
    calculateSurge,
)


@pytest.mark.parametrize(("distance", "weight", "expected"), [
    (2, 1, 2.0), (7, 3, 4.0), (5, 8, 4.5),
    (3, 2, 2.0), (10, 2, 5.5), (10, 6, 7.0),
    (5, 5, 3.0), (0, 0, 2.0), (6, 2, 3.5),
])
def test_delivery_fee_should_follow_tariff(distance, weight, expected):
    assert calculateDeliveryFee(distance, weight) == expected


@pytest.mark.parametrize(("distance", "weight"), [(15, 2), (-1, 2), (3, -1), ("5", 2), (True, 2)])
def test_delivery_fee_should_reject_invalid_distance_or_weight(distance, weight):
    with pytest.raises(ValueError):
        calculateDeliveryFee(distance, weight)


@pytest.mark.parametrize(("subtotal", "code", "expected"), [
    (50, "BIENVENUE20", 40), (30, "FIXE5", 25),
    (15, "BIENVENUE20", 12), (50, "CADEAU100", 0),
    (5, "GROSSE10", 0), (0, None, 0), (10, "", 10),
    (50, None, 50),
])
def test_promo_should_apply_correct_discount(subtotal, code, expected):
    assert applyPromoCode(subtotal, code, PROMO_CODES, date(2026, 11, 21)) == expected


@pytest.mark.parametrize(("subtotal", "code", "error_type"), [
    (25, "EXPIRE", ValueError), (14, "BIENVENUE20", ValueError),
    (30, "INCONNU", LookupError), (-1, None, ValueError),
])
def test_promo_should_reject_invalid_or_expired_code(subtotal, code, error_type):
    with pytest.raises(error_type):
        applyPromoCode(subtotal, code, PROMO_CODES, date(2026, 11, 21))


def test_promo_should_accept_expiration_on_exact_day():
    assert applyPromoCode(50, "BIENVENUE20", PROMO_CODES, date(2099, 12, 31)) == 40


def test_promo_should_reject_after_expiration():
    with pytest.raises(ValueError, match="expiré"):
        applyPromoCode(50, "BIENVENUE20", PROMO_CODES, date(2100, 1, 1))


@pytest.mark.parametrize(("codes", "error_type"), [
    ([{"code": "X", "type": "bogus", "value": 1, "minOrder": 0, "expiresAt": "2099-01-01"}], ValueError),
    ([{"code": "X", "type": "percentage", "value": 101, "minOrder": 0, "expiresAt": "2099-01-01"}], ValueError),
    ([{"code": "X", "type": "fixed", "value": -5, "minOrder": 0, "expiresAt": "2099-01-01"}], ValueError),
])
def test_promo_should_reject_invalid_promo_rule(codes, error_type):
    with pytest.raises(error_type):
        applyPromoCode(50, "X", codes, date(2026, 11, 21))


@pytest.mark.parametrize(("hour", "day", "expected"), [
    (15, "tuesday", 1.0), (12.5, "wednesday", 1.3),
    (20, "thursday", 1.5), (21, "friday", 1.8),
    (14, "sunday", 1.2), (11.5, "tuesday", 1.0),
    (19, "monday", 1.5), (22, "friday", 1.8),
    (9.983, "tuesday", 0), (10, "tuesday", 1.0),
    (23, "friday", 0), ("12:30", "tuesday", 1.3),
    ("10:00", "sunday", 1.2), ("22:01", "sunday", 0),
    ("18:30", "wednesday", 1.0), (20, "saturday", 1.8),
])
def test_surge_should_follow_day_and_hour(hour, day, expected):
    assert calculateSurge(hour, day) == expected


@pytest.mark.parametrize(("hour", "day"), [
    (-1, "monday"), (24, "tuesday"), (12, "funday"),
    ("abc", "monday"), (12, None), (True, "friday"),
    ("22:75", "friday"),
])
def test_surge_should_reject_invalid_day_or_hour(hour, day):
    with pytest.raises(ValueError):
        calculateSurge(hour, day)


PIZZAS = [{"name": "Pizza", "price": 12.50, "quantity": 2}]


def test_total_should_calculate_basic_order():
    result = calculateOrderTotal(PIZZAS, 5, 2, None, 15, "tuesday", today=date(2026, 11, 21))
    assert result == {"subtotal": 25, "discount": 0, "deliveryFee": 3, "surge": 1.0, "total": 28}


def test_total_should_apply_promo_to_items_only():
    result = calculateOrderTotal(PIZZAS, 5, 2, "BIENVENUE20", 15, "tuesday", today=date(2026, 11, 21))
    assert result == {"subtotal": 25, "discount": 5, "deliveryFee": 3, "surge": 1, "total": 23}


def test_total_should_apply_surge_to_delivery_only():
    result = calculateOrderTotal(PIZZAS, 5, 2, None, 20, "friday", today=date(2026, 11, 21))
    assert result == {"subtotal": 25, "discount": 0, "deliveryFee": 5.4, "surge": 1.8, "total": 30.4}


def test_total_should_sum_multiple_items():
    items = PIZZAS + [{"name": "Soda", "price": 2.25, "quantity": 1}]
    result = calculateOrderTotal(items, 2, 1, None, 15, "tuesday", today=date(2026, 11, 21))
    assert result["subtotal"] == 27.25
    assert result["total"] == 29.25


@pytest.mark.parametrize(("items", "distance", "weight", "promo", "hour", "day"), [
    ([], 2, 2, None, 15, "tuesday"),
    ([{"name": "Pizza", "price": 2, "quantity": 0}], 2, 2, None, 15, "tuesday"),
    ([{"name": "Pizza", "price": -2, "quantity": 1}], 2, 2, None, 15, "tuesday"),
    ([{"name": "Pizza", "price": 2, "quantity": 1}], 2, 2, None, 23, "tuesday"),
    ([{"name": "Pizza", "price": 2, "quantity": 1}], 15, 2, None, 15, "tuesday"),
    ([{"name": "Pizza", "price": 2, "quantity": 1}], 2, 2, "EXPIRE", 15, "tuesday"),
    ([{"name": "", "price": 2, "quantity": 1}], 2, 2, None, 15, "tuesday"),
    ([{"name": "Pizza", "price": 2, "quantity": 1.5}], 2, 2, None, 15, "tuesday"),
    (None, 2, 2, None, 15, "tuesday"),
])
def test_total_should_reject_invalid_orders(items, distance, weight, promo, hour, day):
    with pytest.raises(ValueError):
        calculateOrderTotal(items, distance, weight, promo, hour, day, today=date(2026, 11, 21))


def test_total_should_not_add_discount_for_no_promo():
    result = calculateOrderTotal(PIZZAS, 0, 0, "", 10, "monday", today=date(2026, 11, 21))
    assert result["discount"] == 0
    assert result["deliveryFee"] == 2
