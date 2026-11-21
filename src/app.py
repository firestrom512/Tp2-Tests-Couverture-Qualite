"""API Flask: simulation de prix et gestion des commandes en mémoire."""

from datetime import date

from flask import Flask, jsonify, request

from src.pricing import PROMO_CODES, applyPromoCode, calculateOrderTotal
from src.utils import _money


def reset_orders(app):
    """Réinitialiser les commandes: utilisé par les tests et les développeurs."""
    app.config["ORDERS"] = {}
    app.config["NEXT_ID"] = 1


def create_app(today_provider=None):
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    app.config["TODAY_PROVIDER"] = today_provider or date.today
    reset_orders(app)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Requête invalide"}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Ressource introuvable"}), 404

    def compute_order(body):
        if not isinstance(body, dict):
            raise ValueError("Objet JSON attendu")
        required = ("items", "distance", "weight", "hour", "dayOfWeek")
        if any(field not in body for field in required):
            raise ValueError("Champ obligatoire manquant")
        return calculateOrderTotal(
            body["items"], body["distance"], body["weight"],
            body.get("promoCode"), body["hour"], body["dayOfWeek"],
            PROMO_CODES, app.config["TODAY_PROVIDER"](),
        )

    def handle_order_error(error):
        status = 404 if isinstance(error, LookupError) else 400
        return jsonify({"error": str(error)}), status

    @app.post("/orders/simulate")
    def simulate_order():
        try:
            pricing = compute_order(request.get_json(silent=True))
        except (ValueError, LookupError, TypeError, KeyError) as error:
            return handle_order_error(error)
        return jsonify(pricing), 200

    @app.post("/orders")
    def save_order():
        body = request.get_json(silent=True)
        try:
            pricing = compute_order(body)
        except (ValueError, LookupError, TypeError, KeyError) as error:
            return handle_order_error(error)
        order_id = app.config["NEXT_ID"]
        app.config["NEXT_ID"] += 1
        order = {"id": order_id, **body, **pricing}
        app.config["ORDERS"][order_id] = order
        return jsonify(order), 201

    @app.get("/orders/<int:order_id>")
    def get_order(order_id):
        order = app.config["ORDERS"].get(order_id)
        if order is None:
            return jsonify({"error": "Commande introuvable"}), 404
        return jsonify(order), 200

    @app.post("/promo/validate")
    def validate_promo():
        body = request.get_json(silent=True)
        if not isinstance(body, dict) or not body.get("promoCode") or "subtotal" not in body:
            return jsonify({"error": "Code promo et sous-total requis"}), 400
        try:
            subtotal = body["subtotal"]
            final = applyPromoCode(subtotal, body["promoCode"], PROMO_CODES,
                                   app.config["TODAY_PROVIDER"]())
            return jsonify({"valid": True, "subtotal": _money(subtotal),
                            "discount": _money(subtotal - final), "finalTotal": final}), 200
        except (ValueError, TypeError, KeyError, LookupError) as error:
            return handle_order_error(error)

    return app
