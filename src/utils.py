"""Utilitaires de manipulation de chaînes, nombres et collections."""

import math
import re
import unicodedata
from decimal import Decimal, ROUND_HALF_UP


def _money(value):
    """Arrondir à deux décimales de manière prévisible."""
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def capitalize(text):
    if text is None or text == "":
        return ""
    if not isinstance(text, str):
        raise ValueError("Texte invalide")
    return text[0].upper() + text[1:].lower()


def calculateAverage(numbers):
    if numbers is None or numbers == []:
        return 0
    if not isinstance(numbers, list) or any(
        isinstance(n, bool) or not isinstance(n, (int, float)) or not math.isfinite(n)
        for n in numbers
    ):
        raise ValueError("Liste de nombres invalide")
    return _money(sum(numbers) / len(numbers))


def slugify(text):
    if text is None or text == "":
        return ""
    if not isinstance(text, str):
        raise ValueError("Texte invalide")
    normalized = unicodedata.normalize("NFKD", text)
    normalized = "".join(c for c in normalized if not unicodedata.combining(c))
    normalized = normalized.lower().replace("'", "").replace("’", "")
    normalized = re.sub(r"[^a-z0-9\s-]", "", normalized)
    return re.sub(r"[-\s]+", "-", normalized).strip("-")


def clamp(value, minimum, maximum):
    if minimum > maximum:
        raise ValueError("minimum supérieur au maximum")
    return max(minimum, min(value, maximum))


def sortStudents(students, sortBy, order="asc"):
    if students is None or students == []:
        return []
    if sortBy not in {"name", "grade", "age"}:
        raise ValueError("Critère de tri invalide")
    if order not in {"asc", "desc"}:
        raise ValueError("Ordre de tri invalide")
    # sorted crée une nouvelle liste et préserve la liste passée en argument.
    return sorted(students, key=lambda s: s[sortBy], reverse=order == "desc")


def parsePrice(value):
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return _money(value) if math.isfinite(value) and value >= 0 else None
    if not isinstance(value, str):
        return None
    value = value.strip().lower()
    if value == "gratuit":
        return 0
    value = value.replace("€", "").strip().replace(",", ".")
    if not re.fullmatch(r"\d+(?:\.\d+)?", value):
        return None
    return _money(value)


def groupBy(array, key):
    if array is None or array == []:
        return {}
    if not isinstance(array, list) or not isinstance(key, str) or not key:
        raise ValueError("Paramètres invalides")
    result = {}
    for item in array:
        if not isinstance(item, dict):
            raise ValueError("Chaque élément doit être un objet")
        result.setdefault(item.get(key), []).append(item)
    return result


def calculateDiscount(price, discountRules):
    """Appliquer les réductions dans l'ordre, sans rendre le prix négatif.

    Pour buyXgetY, le nombre d'articles est inféré du prix courant / itemPrice.
    Exemple: 4 articles de 10€, règle buy=3/free=1 -> réduction de 10€.
    """
    if isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price) or price < 0:
        raise ValueError("Prix invalide")
    if not isinstance(discountRules, list):
        raise ValueError("Règles invalides")
    total = Decimal(str(price))
    for rule in discountRules:
        if not isinstance(rule, dict):
            raise ValueError("Règle invalide")
        kind = rule.get("type")
        if kind in {"percentage", "fixed"}:
            value = rule.get("value")
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError("Réduction invalide")
            if kind == "percentage":
                if value > 100:
                    raise ValueError("Pourcentage invalide")
                total *= 1 - Decimal(str(value)) / 100
            else:
                total = max(Decimal(0), total - Decimal(str(value)))
        elif kind == "buyXgetY":
            buy, free, item_price = rule.get("buy"), rule.get("free"), rule.get("itemPrice")
            if (not isinstance(buy, int) or isinstance(buy, bool) or buy <= 0
                or not isinstance(free, int) or isinstance(free, bool) or free <= 0
                or isinstance(item_price, bool) or not isinstance(item_price, (int, float))
                or not math.isfinite(item_price) or item_price <= 0):
                raise ValueError("Offre buyXgetY invalide")
            count = int(total / Decimal(str(item_price)))
            groups = count // (buy + free)
            total = max(Decimal(0), total - groups * free * Decimal(str(item_price)))
        else:
            raise ValueError("Type de réduction inconnu")
    return _money(total)
