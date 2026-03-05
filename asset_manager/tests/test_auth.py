import pytest
from datetime import datetime
from app.models import User
from app import db


@pytest.mark.integration
def test_register_and_login(client, app):
    response = client.post(
        "/register",
        data={
            "username": "testuser",
            "password": "Testpass#123",
            "confirm_password": "Testpass#123",
        },
        follow_redirects=True,
    )
    assert b"Login" in response.data

    response = client.post(
        "/login",
        data={"username": "testuser", "password": "Testpass#123"},
        follow_redirects=True,
    )
    assert b"Assets List" in response.data


@pytest.mark.integration
def test_invalid_login(client):
    response = client.post(
        "/login",
        data={"username": "admin", "password": "wrongpass"},
        follow_redirects=True,
    )
    assert b"Invalid credentials" in response.data


@pytest.mark.integration
def test_access_protected_route_without_login(client):
    response = client.get("/assets", follow_redirects=True)
    assert b"Login" in response.data


@pytest.mark.integration
def test_register_rejects_short_username(client):
    response = client.post(
        "/register",
        data={
            "username": "ab",
            "password": "Strongpass#123",
            "confirm_password": "Strongpass#123",
        },
        follow_redirects=True,
    )
    assert b"Field must be between 3 and 150 characters long." in response.data


@pytest.mark.security
def test_weak_password_rejected(client):
    response = client.post(
        "/register",
        data={
            "username": "weakuser",
            "password": "weak",
            "confirm_password": "weak",
        },
        follow_redirects=True,
    )
    assert b"Password must be at least 10 characters long." in response.data


@pytest.mark.security
def test_login_lockout_after_failed_attempts(client, app):
    for _ in range(5):
        client.post(
            "/login",
            data={"username": "admin", "password": "wrongpass"},
            follow_redirects=True,
        )

    locked_response = client.post(
        "/login",
        data={"username": "admin", "password": "Admin#12345"},
        follow_redirects=True,
    )
    assert b"Account temporarily locked" in locked_response.data

    with app.app_context():
        admin = User.query.filter_by(username="admin").first()
        assert admin is not None
        assert admin.locked_until is not None


@pytest.mark.security
def test_login_succeeds_after_lockout_expiry(client, app):
    with app.app_context():
        admin = User.query.filter_by(username="admin").first()
        assert admin is not None
        admin.locked_until = datetime(2000, 1, 1)
        db.session.commit()

    response = client.post(
        "/login",
        data={"username": "admin", "password": "Admin#12345"},
        follow_redirects=True,
    )
    assert b"Logged in successfully!" in response.data


@pytest.mark.security
def test_login_sql_injection_payload_rejected(client):
    response = client.post(
        "/login",
        data={"username": "' OR 1=1 --", "password": "anything"},
        follow_redirects=True,
    )
    assert b"Invalid credentials" in response.data


@pytest.mark.security
def test_logout_get_method_not_allowed(client):
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 405
