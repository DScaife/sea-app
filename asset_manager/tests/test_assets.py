import pytest
from app.models import Asset
from app import db
from datetime import datetime


def login(client, username, password):
    """Helper function to log in a user."""
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def logout(client):
    """Helper function to log out a user."""
    return client.post("/logout", follow_redirects=True)


@pytest.mark.integration
def test_new_asset_regular_user(client, app):
    client.post(
        "/register",
        data={
            "username": "regularuser",
            "password": "Regular#12345",
            "confirm_password": "Regular#12345",
        },
        follow_redirects=True,
    )
    login(client, "regularuser", "Regular#12345")

    response = client.post(
        "/asset/new",
        data={
            "name": "Laptop",
            "category": "Electronics",
            "purchase_date": "2025-06-13",
        },
        follow_redirects=True,
    )
    assert b"Pending Approval" in response.data
    assert b"Laptop" in response.data


@pytest.mark.integration
def test_edit_asset(client, app):
    client.post(
        "/register",
        data={
            "username": "edituser",
            "password": "Edituser#123",
            "confirm_password": "Edituser#123",
        },
        follow_redirects=True,
    )
    login(client, "edituser", "Edituser#123")

    client.post(
        "/asset/new",
        data={
            "name": "Old Laptop",
            "category": "Electronics",
            "purchase_date": "2025-06-13",
        },
        follow_redirects=True,
    )

    with app.app_context():
        asset = Asset.query.filter_by(name="Old Laptop").first()
        assert asset is not None, "Asset was not found!"
        asset_id = asset.id

    response = client.post(
        f"/asset/edit/{asset_id}",
        data={
            "name": "Updated Laptop",
            "category": "Electronics",
            "purchase_date": "2025-06-13",
            "status": "Pending Approval",
        },
        follow_redirects=True,
    )
    assert b"Updated Laptop" in response.data


@pytest.mark.integration
def test_asset_approval(client, app):
    login(client, "admin", "Admin#12345")

    asset = Asset(
        name="Test Device",
        category="Gadget",
        purchase_date=datetime.strptime("2025-06-13", "%Y-%m-%d").date(),
        status="Pending Approval",
        user_id=1,
    )
    with app.app_context():
        db.session.add(asset)
        db.session.commit()
        asset_id = asset.id

    response = client.post(f"/asset/approve/{asset_id}", follow_redirects=True)
    assert b"Active" in response.data
    assert b"Test Device" in response.data


@pytest.mark.integration
def test_asset_rejection(client, app):
    login(client, "admin", "Admin#12345")

    asset = Asset(
        name="Faulty Device",
        category="Gadget",
        purchase_date=datetime.strptime("2025-06-13", "%Y-%m-%d").date(),
        status="Pending Approval",
        user_id=1,
    )
    with app.app_context():
        db.session.add(asset)
        db.session.commit()
        asset_id = asset.id

    response = client.post(f"/asset/reject/{asset_id}", follow_redirects=True)
    assert b"Rejected" in response.data
    assert b"Faulty Device" in response.data


@pytest.mark.security
def test_regular_user_cannot_approve_asset(client, app):
    client.post(
        "/register",
        data={
            "username": "normaluser",
            "password": "Normaluser#123",
            "confirm_password": "Normaluser#123",
        },
        follow_redirects=True,
    )
    login(client, "normaluser", "Normaluser#123")

    with app.app_context():
        pending_asset = Asset(
            name="Approval Attempt",
            category="Device",
            purchase_date=datetime.strptime("2025-06-13", "%Y-%m-%d").date(),
            status="Pending Approval",
            user_id=1,
        )
        db.session.add(pending_asset)
        db.session.commit()
        asset_id = pending_asset.id

    response = client.post(f"/asset/approve/{asset_id}", follow_redirects=True)
    assert b"Access denied." in response.data

    with app.app_context():
        asset = db.session.get(Asset, asset_id)
        assert asset.status == "Pending Approval"
