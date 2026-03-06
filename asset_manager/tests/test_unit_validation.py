import pytest
from datetime import date, timedelta
from wtforms.validators import ValidationError

from app.forms import validate_password_strength, validate_not_future_date


class DummyField:
    def __init__(self, data):
        self.data = data


@pytest.mark.unit
def test_password_strength_accepts_valid_password():
    field = DummyField("StrongPass#123")
    validate_password_strength(None, field)


@pytest.mark.unit
def test_password_strength_rejects_weak_password():
    field = DummyField("weak")
    with pytest.raises(ValidationError):
        validate_password_strength(None, field)


@pytest.mark.unit
def test_purchase_date_validator_rejects_future_date():
    future = date.today() + timedelta(days=1)
    field = DummyField(future)
    with pytest.raises(ValidationError):
        validate_not_future_date(None, field)


@pytest.mark.unit
def test_purchase_date_validator_allows_today_date():
    today = date.today()
    field = DummyField(today)
    validate_not_future_date(None, field)