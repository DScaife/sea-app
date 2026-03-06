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


@pytest.mark.integration
def test_admin_filters_assets_by_status_and_user(client, app):
    client.post(
        "/register",
        data={
            "username": "filteruser",
            "password": "Filteruser#123",
            "confirm_password": "Filteruser#123",
        },
        follow_redirects=True,
    )

    with app.app_context():
        user_asset = Asset(
            name="Filter Match",
            category="Laptop",
            purchase_date=datetime.strptime("2025-06-13", "%Y-%m-%d").date(),
            status="Active",
            user_id=2,
        )
        non_match_asset = Asset(
            name="Filter Miss",
            category="Laptop",
            purchase_date=datetime.strptime("2025-06-13", "%Y-%m-%d").date(),
            status="Rejected",
            user_id=1,
        )
        db.session.add(user_asset)
        db.session.add(non_match_asset)
        db.session.commit()

    login(client, "admin", "Admin#12345")
    response = client.get("/assets?status=Active&user=filteruser", follow_redirects=True)
    assert b"Filter Match" in response.data
    assert b"Filter Miss" not in response.data


@pytest.mark.integration
def test_new_asset_rejects_future_purchase_date(client):
    client.post(
        "/register",
        data={
            "username": "futureuser",
            "password": "Futureuser#123",
            "confirm_password": "Futureuser#123",
        },
        follow_redirects=True,
    )
    login(client, "futureuser", "Futureuser#123")

    response = client.post(
        "/asset/new",
        data={
            "name": "Future Asset",
            "category": "Electronics",
            "purchase_date": "2099-01-01",
        },
        follow_redirects=True,
    )
    assert b"Purchase date cannot be in the future." in response.data


@pytest.mark.security
def test_regular_user_cannot_delete_other_users_asset(client, app):
    client.post(
        "/register",
        data={
            "username": "deleteruser",
            "password": "Deleteruser#123",
            "confirm_password": "Deleteruser#123",
        },
        follow_redirects=True,
    )
    login(client, "deleteruser", "Deleteruser#123")

    with app.app_context():
        admin_owned_asset = Asset(
            name="Cannot Delete",
            category="Device",
            purchase_date=datetime.strptime("2025-06-13", "%Y-%m-%d").date(),
            status="Active",
            user_id=1,
        )
        db.session.add(admin_owned_asset)
        db.session.commit()
        asset_id = admin_owned_asset.id

    response = client.post(f"/asset/delete/{asset_id}", follow_redirects=True)
    assert b"Access denied." in response.data


@pytest.mark.integration
def test_non_admin_edit_forces_pending_approval_status(client, app):
    client.post(
        "/register",
        data={
            "username": "statususer",
            "password": "Statususer#123",
            "confirm_password": "Statususer#123",
        },
        follow_redirects=True,
    )
    login(client, "statususer", "Statususer#123")

    with app.app_context():
        own_asset = Asset(
            name="Status Target",
            category="Device",
            purchase_date=datetime.strptime("2025-06-13", "%Y-%m-%d").date(),
            status="Active",
            user_id=2,
        )
        db.session.add(own_asset)
        db.session.commit()
        asset_id = own_asset.id

    client.post(
        f"/asset/edit/{asset_id}",
        data={
            "name": "Status Target Updated",
            "category": "Device",
            "purchase_date": "2025-06-13",
            "status": "Active",
        },
        follow_redirects=True,
    )

    with app.app_context():
        updated = db.session.get(Asset, asset_id)
        assert updated.status == "Pending Approval"


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
