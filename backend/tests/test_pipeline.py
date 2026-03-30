from decimal import Decimal

from app.models.movement import MovementType
from app.services.pipeline import _parse_amount, _parse_datetime, _parse_movement_type


def test_parse_movement_type_expense():
    assert _parse_movement_type("expense") == MovementType.EXPENSE


def test_parse_movement_type_income():
    assert _parse_movement_type("income") == MovementType.INCOME


def test_parse_movement_type_transfer():
    assert _parse_movement_type("transfer") == MovementType.TRANSFER


def test_parse_movement_type_unknown_defaults_expense():
    assert _parse_movement_type("unknown") == MovementType.EXPENSE


def test_parse_amount_valid():
    assert _parse_amount(450.00) == Decimal("450.00")
    assert _parse_amount("199.99") == Decimal("199.99")
    assert _parse_amount(0) == Decimal("0.00")


def test_parse_amount_none():
    assert _parse_amount(None) is None


def test_parse_amount_invalid():
    assert _parse_amount("not_a_number") is None


def test_parse_datetime_iso():
    dt = _parse_datetime("2026-03-29T14:30:00")
    assert dt is not None
    assert dt.year == 2026
    assert dt.month == 3
    assert dt.day == 29


def test_parse_datetime_date_only():
    dt = _parse_datetime("2026-03-29")
    assert dt is not None
    assert dt.year == 2026


def test_parse_datetime_none():
    assert _parse_datetime(None) is None


def test_parse_datetime_invalid():
    assert _parse_datetime("not a date") is None
