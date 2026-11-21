"""Moteur de tarification pour la livraison de repas."""

import math
from datetime import date
from decimal import Decimal

from src.utils import _money


PROMO_CODES = [
    {"code": "BIENVENUE20", "type": "percentage", "value": 20,
     "minOrder": 15.0, "expiresAt": "2099-12-31"},
    {"code": "FIXE5", "type": "fixed", "value": 5,
     "minOrder": 10.0, "expiresAt": "2099-12-31"},
    {"code": "CADEAU100", "type": "percentage", "value": 100,
     "minOrder": 0.0, "expiresAt": "2099-12-31"},
    {"code": "GROSSE10", "type": "fixed", "value": 10,
     "minOrder": 0.0, "expiresAt": "2099-12-31"},
    {"code": "EXPIRE", "type": "percentage", "value": 20,
     "minOrder": 0.0, "expiresAt": "2000-01-01"},
]


def _nonnegative_number(value, label):
    if (isinstance(value, bool) or not isinstance(value, (int, float))
        or not math.isfinite(value) or value < 0):
        raise ValueError(f"{label} invalide")
    return value


def calculateDeliveryFee(distance, weight):
    _nonnegative_number(distance, "Distance")
    _nonnegative_number(weight, "Poids")
    if distance > 10:
        raise ValueError("Livraison hors zone")
    return _money(Decimal("2.00") + Decimal(str(max(0, distance - 3))) * Decimal("0.50")
                  + (Decimal("1.50") if weight > 5 else Decimal(0)))


def applyPromoCode(subtotal, promoCode, promoCodes, today=None):
    _nonnegative_number(subtotal, "Sous-total")
    if promoCode is None or promoCode == "":
        return _money(subtotal)
    if not isinstance(promoCode, str) or not isinstance(promoCodes, list):
        raise ValueError("Code promo invalide")
    promo = next((p for p in promoCodes if p.get("code") == promoCode), None)
    if promo is None:
        raise LookupError("Code promo inconnu")
    today = today or date.today()
    if isinstance(today, str):
        today = date.fromisoformat(today)
    if today > date.fromisoformat(promo["expiresAt"]):
        raise ValueError("Code promo expiré")
    if subtotal < promo["minOrder"]:
        raise ValueError("Montant minimum non atteint")
    reduction_type = promo["type"]
    if reduction_type == "percentage":
        if not 0 <= promo["value"] <= 100:
            raise ValueError("Pourcentage de réduction invalide")
        reduction = Decimal(str(subtotal)) * Decimal(str(promo["value"])) / 100
    elif reduction_type == "fixed":
        if promo["value"] < 0:
            raise ValueError("Réduction négative")
        reduction = Decimal(str(promo["value"]))
    else:
        raise ValueError("Type de réduction inconnu")
    return _money(max(Decimal(0), Decimal(str(subtotal)) - reduction))


def _hour_number(hour):
    if isinstance(hour, str):
        try:
            h, minute = hour.split(":")
            h, minute = int(h), int(minute)
            if 0 <= h <= 23 and 0 <= minute <= 59:
                return h + minute / 60
        except (ValueError, TypeError):
            pass
        raise ValueError("Heure invalide")
    if isinstance(hour, bool) or not isinstance(hour, (int, float)) or not math.isfinite(hour) or not 0 <= hour < 24:
        raise ValueError("Heure invalide")
    return hour


def calculateSurge(hour, dayOfWeek):
    hour = _hour_number(hour)
    if not isinstance(dayOfWeek, str):
        raise ValueError("Jour invalide")
    day = dayOfWeek.lower()
    if day not in {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}:
        raise ValueError("Jour invalide")
    if hour < 10 or hour > 22:
        return 0
    if day == "sunday":
        return 1.2
    if day in {"friday", "saturday"} and 19 <= hour <= 22:
        return 1.8
    if day in {"monday", "tuesday", "wednesday", "thursday"}:
        if 12 <= hour <= 13.5:
            return 1.3
        if 19 <= hour <= 21:
            return 1.5
    return 1.0


def calculateOrderTotal(items, distance, weight, promoCode, hour, dayOfWeek,
                        promoCodes=None, today=None):
    if not isinstance(items, list) or not items:
        raise ValueError("Panier vide")
    subtotal = Decimal(0)
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not item["name"].strip():
            raise ValueError("Article invalide")
        price = _nonnegative_number(item.get("price"), "Prix")
        qty = item.get("quantity")
        if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
            raise ValueError("Quantité invalide")
        subtotal += Decimal(str(price)) * qty
    subtotal = _money(subtotal)
    surge = calculateSurge(hour, dayOfWeek)
    if surge == 0:
        raise ValueError("Restaurant fermé")
    base_delivery_fee = calculateDeliveryFee(distance, weight)
    after_promo = applyPromoCode(subtotal, promoCode, promoCodes if promoCodes is not None else PROMO_CODES, today)
    discount = _money(Decimal(str(subtotal)) - Decimal(str(after_promo)))
    delivery_fee = _money(Decimal(str(base_delivery_fee)) * Decimal(str(surge)))
    total = _money(Decimal(str(after_promo)) + Decimal(str(delivery_fee)))
    return {"subtotal": subtotal, "discount": discount, "deliveryFee": delivery_fee,
            "surge": surge, "total": total}
