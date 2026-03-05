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
