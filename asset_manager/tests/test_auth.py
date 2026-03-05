from app.models import User


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


def test_invalid_login(client):
    response = client.post(
        "/login",
        data={"username": "admin", "password": "wrongpass"},
        follow_redirects=True,
    )
    assert b"Invalid credentials" in response.data


def test_access_protected_route_without_login(client):
    response = client.get("/assets", follow_redirects=True)
    assert b"Login" in response.data


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


def test_login_sql_injection_payload_rejected(client):
    response = client.post(
        "/login",
        data={"username": "' OR 1=1 --", "password": "anything"},
        follow_redirects=True,
    )
    assert b"Invalid credentials" in response.data
