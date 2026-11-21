"""Validation des informations utilisateurs."""

import re


def isValidEmail(email):
    if not isinstance(email, str):
        return False
    return bool(re.fullmatch(r"[^\s@]+@[^\s@.]+(?:\.[^\s@.]+)+", email))


def isValidPassword(password):
    errors = []
    if not isinstance(password, str):
        password = ""
    if len(password) < 8:
        errors.append("Minimum 8 caractères")
    if not re.search(r"[A-Z]", password):
        errors.append("Majuscule manquante")
    if not re.search(r"[a-z]", password):
        errors.append("Minuscule manquante")
    if not re.search(r"\d", password):
        errors.append("Chiffre manquant")
    if not re.search(r"[!@#$%^&*]", password):
        errors.append("Caractère spécial manquant")
    return {"valid": not errors, "errors": errors}


def isValidAge(age):
    return isinstance(age, int) and not isinstance(age, bool) and 0 <= age <= 150
