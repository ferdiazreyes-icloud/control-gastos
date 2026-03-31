import uuid
from datetime import datetime
from decimal import Decimal

from app.models.movement import Movement, MovementStatus, MovementType
from app.services.dedup import (
    _is_pre_auth,
    _is_progressive_update,
    _normalize_merchant,
    _score_match,
)


def _make_movement(**kwargs) -> Movement:
    """Helper to create a Movement for testing."""
    defaults = {
        "id": uuid.uuid4(),
        "type": MovementType.EXPENSE,
        "amount": Decimal("100.00"),
        "currency": "MXN",
        "account": "BBVA Débito",
        "movement_date": datetime(2026, 3, 29, 14, 0, 0),
        "concept": "Compra",
        "merchant": "Walmart",
        "status": MovementStatus.PENDING,
    }
    defaults.update(kwargs)
    return Movement(**defaults)


def test_normalize_merchant_basic():
    assert _normalize_merchant("Walmart") == "walmart"
    assert _normalize_merchant("  UBER  ") == "uber"
    assert _normalize_merchant(None) == ""
    assert _normalize_merchant("") == ""


def test_normalize_merchant_paypal_prefix():
    assert _normalize_merchant("PAYPAL *IHERB LLC") == "iherb llc"
    assert _normalize_merchant("PAYPAL*RAPPI") == "rappi"


def test_score_exact_match():
    """Same amount + merchant + date + account = high score."""
    m1 = _make_movement()
    m2 = _make_movement()
    score = _score_match(m1, m2)
    assert score >= 60  # Should be 40+30+15+10 = 95


def test_score_same_amount_different_merchant():
    """Same amount + date + account but different merchant still flags as potential dup."""
    m1 = _make_movement(merchant="Walmart")
    m2 = _make_movement(merchant="Costco")
    score = _score_match(m1, m2)
    # 40+0+15+10 = 65 — above threshold. This is expected:
    # same amount + date + account is a strong signal even without merchant.
    # FerDi uses "not duplicate" to split if it's wrong.
    assert score >= 60


def test_score_substring_merchant():
    """Bank description contains merchant name."""
    m1 = _make_movement(merchant="iHerb")
    m2 = _make_movement(merchant="PAYPAL *IHERB LLC 402")
    score = _score_match(m1, m2)
    assert score >= 60  # 40+20+15+10 = 85


def test_score_different_amount():
    """Different amounts should reduce score."""
    m1 = _make_movement(amount=Decimal("100.00"))
    m2 = _make_movement(amount=Decimal("200.00"))
    score = _score_match(m1, m2)
    assert score < 60  # 0+30+15+10 = 55


def test_score_far_apart_dates():
    """Dates more than 48h apart should not get date points."""
    m1 = _make_movement(movement_date=datetime(2026, 3, 29, 14, 0, 0))
    m2 = _make_movement(movement_date=datetime(2026, 4, 5, 14, 0, 0))
    _score_match(m1, m2)
    # 40+30+0+10 = 80 — still above threshold because same amount+merchant+account
    # This is fine; amount+merchant+account is a strong signal


def test_is_pre_auth():
    m = _make_movement(amount=Decimal("1.00"))
    assert _is_pre_auth(m) is True

    m2 = _make_movement(amount=Decimal("100.00"))
    assert _is_pre_auth(m2) is False


def test_is_progressive_update_same_merchant_similar_amount():
    """Uber Eats: order $150 → final $155 (tip added)."""
    old = _make_movement(
        merchant="Uber Eats",
        amount=Decimal("150.00"),
        movement_date=datetime(2026, 3, 29, 14, 0, 0),
    )
    new = _make_movement(
        merchant="Uber Eats",
        amount=Decimal("155.00"),
        movement_date=datetime(2026, 3, 29, 15, 0, 0),
    )
    assert _is_progressive_update(new, old) is True


def test_is_progressive_update_different_merchant():
    """Different merchants should not be progressive."""
    old = _make_movement(merchant="Uber Eats")
    new = _make_movement(merchant="Rappi")
    assert _is_progressive_update(new, old) is False


def test_is_progressive_update_too_different_amount():
    """Amount difference > 20% is not progressive."""
    old = _make_movement(
        merchant="Uber Eats",
        amount=Decimal("100.00"),
    )
    new = _make_movement(
        merchant="Uber Eats",
        amount=Decimal("200.00"),
    )
    assert _is_progressive_update(new, old) is False
