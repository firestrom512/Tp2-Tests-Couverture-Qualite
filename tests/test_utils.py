"""Parties A1, A4 et bonus A5-A7 : tests unitaires des utilitaires."""

import pytest

from src.utils import (
    calculateAverage,
    calculateDiscount,
    capitalize,
    clamp,
    groupBy,
    parsePrice,
    slugify,
    sortStudents,
)


@pytest.mark.parametrize(("input_value", "expected"), [
    ("hello", "Hello"), ("WORLD", "World"), ("", ""), (None, ""),
    ("mIxEd", "Mixed"), ("a", "A"),
])
def test_capitalize_should_format_first_letter_when_string(input_value, expected):
    assert capitalize(input_value) == expected


def test_capitalize_should_reject_nonstring():
    with pytest.raises(ValueError):
        capitalize(4)


@pytest.mark.parametrize(("input_value", "expected"), [
    ([10, 12, 14], 12), ([15], 15), ([], 0), ([10, 11, 12], 11),
    (None, 0), ([10, 11], 10.5), ([1, 1, 2], 1.33),
])
def test_average_should_calculate_when_given_list(input_value, expected):
    assert calculateAverage(input_value) == expected


@pytest.mark.parametrize("bad", ["test", [1, "x"], [True, 2], [float("inf")]])
def test_average_should_reject_invalid_numbers(bad):
    with pytest.raises(ValueError):
        calculateAverage(bad)


@pytest.mark.parametrize(("input_value", "expected"), [
    ("Hello World", "hello-world"),
    (" Spaces Everywhere ", "spaces-everywhere"),
    ("C'est l'ete !", "cest-lete"),
    ("", ""), ("Crème brûlée !", "creme-brulee"), (None, ""),
])
def test_slugify_should_convert_text_when_valid(input_value, expected):
    assert slugify(input_value) == expected


def test_slugify_should_reject_number():
    with pytest.raises(ValueError):
        slugify(25)


@pytest.mark.parametrize(("value", "minimum", "maximum", "expected"), [
    (5, 0, 10, 5), (-5, 0, 10, 0), (15, 0, 10, 10), (0, 0, 0, 0),
    (10, 0, 10, 10),
])
def test_clamp_should_limit_value_when_outside_bounds(value, minimum, maximum, expected):
    assert clamp(value, minimum, maximum) == expected


def test_clamp_should_reject_inverted_bounds():
    with pytest.raises(ValueError):
        clamp(5, 10, 0)


STUDENTS = [
    {"name": "Zoé", "grade": 12, "age": 21},
    {"name": "Alice", "grade": 18, "age": 19},
    {"name": "Bob", "grade": 8, "age": 23},
]


def test_sort_should_sort_students_by_grade_ascending():
    assert [s["grade"] for s in sortStudents(STUDENTS, "grade")] == [8, 12, 18]


def test_sort_should_sort_students_by_grade_descending():
    assert [s["grade"] for s in sortStudents(STUDENTS, "grade", "desc")] == [18, 12, 8]


def test_sort_should_sort_students_by_name_ascending():
    assert [s["name"] for s in sortStudents(STUDENTS, "name")] == ["Alice", "Bob", "Zoé"]


def test_sort_should_sort_students_by_age_ascending():
    assert [s["age"] for s in sortStudents(STUDENTS, "age")] == [19, 21, 23]


def test_sort_should_return_empty_when_null():
    assert sortStudents(None, "grade") == []


def test_sort_should_return_empty_when_empty():
    assert sortStudents([], "grade") == []


def test_sort_should_not_modify_original_array():
    copy = [dict(s) for s in STUDENTS]
    result = sortStudents(STUDENTS, "grade")
    assert STUDENTS == copy
    assert result is not STUDENTS


def test_sort_should_default_to_ascending():
    assert sortStudents(STUDENTS, "age") == sortStudents(STUDENTS, "age", "asc")


@pytest.mark.parametrize("criterion", ["unknown", ""]) 
def test_sort_should_reject_invalid_sort_key(criterion):
    with pytest.raises(ValueError):
        sortStudents(STUDENTS, criterion)


def test_sort_should_reject_invalid_order():
    with pytest.raises(ValueError):
        sortStudents(STUDENTS, "grade", "sideways")


@pytest.mark.parametrize(("raw", "expected"), [
    ("12.99", 12.99), ("12,99", 12.99), ("12.99 €", 12.99),
    ("€12.99", 12.99), (12.99, 12.99), ("gratuit", 0),
    ("abc", None), ("-5.00", None), (None, None),
    (False, None), ("0", 0), (float("inf"), None),
])
def test_parse_price_should_return_expected_amount(raw, expected):
    assert parsePrice(raw) == expected


def test_group_by_should_group_roles():
    items = [{"name": "Alice", "role": "dev"}, {"name": "Bob", "role": "design"},
             {"name": "Charlie", "role": "dev"}]
    groups = groupBy(items, "role")
    assert [i["name"] for i in groups["dev"]] == ["Alice", "Charlie"]
    assert [i["name"] for i in groups["design"]] == ["Bob"]


@pytest.mark.parametrize("items", [None, []])
def test_group_by_should_return_empty_when_no_items(items):
    assert groupBy(items, "role") == {}


def test_group_by_should_group_missing_key_under_none():
    assert groupBy([{"name": "Alice"}], "role") == {None: [{"name": "Alice"}]}


@pytest.mark.parametrize(("items", "key"), [(42, "role"), ([1], "role"), ([{}], "")])
def test_group_by_should_reject_invalid_input(items, key):
    with pytest.raises(ValueError):
        groupBy(items, key)


@pytest.mark.parametrize(("price", "rules", "expected"), [
    (100, [{"type": "percentage", "value": 10}], 90),
    (20, [{"type": "fixed", "value": 5}], 15),
    (3, [{"type": "fixed", "value": 5}], 0),
    (100, [{"type": "percentage", "value": 10}, {"type": "fixed", "value": 5}], 85),
    (40, [{"type": "buyXgetY", "buy": 3, "free": 1, "itemPrice": 10}], 30),
    (30, [{"type": "buyXgetY", "buy": 3, "free": 1, "itemPrice": 10}], 30),
    (0, [], 0),
])
def test_calculate_discount_should_apply_rules_in_order(price, rules, expected):
    assert calculateDiscount(price, rules) == expected


@pytest.mark.parametrize(("price", "rules"), [
    (-1, []), (10, None), (10, [{"type": "unknown"}]),
    (10, [{"type": "percentage", "value": 150}]),
    (10, [{"type": "fixed", "value": -1}]),
    (10, [{"type": "buyXgetY", "buy": 0, "free": 1, "itemPrice": 10}]),
    (10, [{"type": "buyXgetY", "buy": 3, "free": 0, "itemPrice": 10}]),
    (10, [{"type": "buyXgetY", "buy": 3, "free": 1, "itemPrice": 0}]),
    (10, ["invalid"]), (True, []),
])
def test_calculate_discount_should_reject_invalid_rules(price, rules):
    with pytest.raises(ValueError):
        calculateDiscount(price, rules)
