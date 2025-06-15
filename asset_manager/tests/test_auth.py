def test_register_and_login(client, app):
    response = client.post(
        "/register",
        data={
            "username": "testuser",
            "password": "testpass",
            "confirm_password": "testpass",
        },
        follow_redirects=True,
    )
    assert b"Login" in response.data

    response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpass"},
        follow_redirects=True,
    )
    assert b"Assets List" in response.data


def test_invalid_login(client):
    response = client.post(
        "/login",
        data={"username": "admin1234", "password": "wrongpass"},
        follow_redirects=True,
    )
    assert b"Invalid credentials" in response.data


def test_access_protected_route_without_login(client):
    response = client.get("/assets", follow_redirects=True)
    assert b"Login" in response.data
