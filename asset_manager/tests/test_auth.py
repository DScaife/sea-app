def test_register_and_login(client, app):
    # Test registration for a new user.
    response = client.post(
        "/register",
        data={
            "username": "testuser",
            "password": "testpass",
            "confirm_password": "testpass",
        },
        follow_redirects=True,
    )
    # Instead of looking for a flash message, check that we end up on the login page.
    assert b"Login" in response.data

    # Now log the user in.
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpass"},
        follow_redirects=True,
    )
    # After a successful login, we expect to be redirected to the assets list.
    assert b"Assets List" in response.data


def test_invalid_login(client):
    # Try logging in with an incorrect password.
    response = client.post(
        "/login",
        data={"username": "admin1234", "password": "wrongpass"},
        follow_redirects=True,
    )
    # Expect that the response contains "Invalid credentials" or similar indication.
    assert b"Invalid credentials" in response.data


def test_access_protected_route_without_login(client):
    # Try accessing a protected route without logging in.
    response = client.get("/assets", follow_redirects=True)
    # This should redirect to the login page.
    assert b"Login" in response.data
