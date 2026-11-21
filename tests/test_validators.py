"""Partie A2 : validateurs et cas limites."""

import pytest

from src.validators import isValidAge, isValidEmail, isValidPassword


@pytest.mark.parametrize(("email", "valid"), [
    ("user@example.com", True),
    ("user.name+tag@domain.co", True),
    ("invalid", False),
    ("@domain.com", False),
    ("user@", False),
    ("", False),
    (None, False),
    ("user@domain", False),
    ("user @domain.com", False),
    ("user@.com", False),
])
def test_email_should_validate_format_when_given_input(email, valid):
    assert isValidEmail(email) is valid


@pytest.mark.parametrize("password", ["Passw0rd!", "Strong123@", "Xy12!abcd"])
def test_password_should_be_valid_when_all_rules_pass(password):
    assert isValidPassword(password) == {"valid": True, "errors": []}


@pytest.mark.parametrize(("password", "errors"), [
    ("short", ["Minimum 8 caractères", "Majuscule manquante", "Chiffre manquant", "Caractère spécial manquant"]),
    ("alllowercase1!", ["Majuscule manquante"]),
    ("ALLUPPERCASE1!", ["Minuscule manquante"]),
    ("NoDigits!here", ["Chiffre manquant"]),
    ("NoSpecial1here", ["Caractère spécial manquant"]),
    ("", ["Minimum 8 caractères", "Majuscule manquante", "Minuscule manquante", "Chiffre manquant", "Caractère spécial manquant"]),
    (None, ["Minimum 8 caractères", "Majuscule manquante", "Minuscule manquante", "Chiffre manquant", "Caractère spécial manquant"]),
])
def test_password_should_report_exact_errors_when_rule_missing(password, errors):
    result = isValidPassword(password)
    assert result["valid"] is False
    assert result["errors"] == errors


@pytest.mark.parametrize(("age", "valid"), [
    (25, True), (0, True), (150, True), (-1, False),
    (151, False), (25.5, False), ("25", False), (None, False),
    (True, False),
])
def test_age_should_accept_only_integer_between_zero_and_150(age, valid):
    assert isValidAge(age) is valid
