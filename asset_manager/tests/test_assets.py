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
    return client.get("/logout", follow_redirects=True)

def test_new_asset_regular_user(client, app):
    # First, register a regular user.
    client.post(
        "/register",
        data={
            "username": "regularuser",
            "password": "testpass",
            "confirm_password": "testpass",
        },
        follow_redirects=True,
    )
    # Login as the regular user.
    login(client, "regularuser", "testpass")

    # Create a new asset.
    response = client.post(
        "/asset/new",
        data={
            "name": "Laptop",
            "category": "Electronics",
            "purchase_date": "2025-06-13",
        },
        follow_redirects=True,
    )
    # Regular user's new asset should have a status of Pending Approval.
    assert b"Pending Approval" in response.data
    assert b"Laptop" in response.data

def test_edit_asset(client, app):
    # Register and log in as a regular user.
    client.post(
        "/register",
        data={
            "username": "edituser",
            "password": "editpass",
            "confirm_password": "editpass",
        },
        follow_redirects=True,
    )
    login(client, "edituser", "editpass")

    # Create an asset.
    client.post(
        "/asset/new",
        data={
            "name": "Old Laptop",
            "category": "Electronics",
            "purchase_date": "2025-06-13",
        },
        follow_redirects=True,
    )

    # Retrieve the asset from the database using an application context.
    with app.app_context():
        asset = Asset.query.filter_by(name="Old Laptop").first()
        # Ensure that we got back an asset.
        assert asset is not None, "Asset was not found!"
        asset_id = asset.id

    # Now simulate editing the asset by using its actual id.
    response = client.post(
        f"/asset/edit/{asset_id}",
        data={
            "name": "Updated Laptop",
            "category": "Electronics",
            "purchase_date": "2025-06-13",
            "status": "Pending Approval",  # Regular user typically doesn't update status.
        },
        follow_redirects=True,
    )
    # Verify that the page shows the updated asset name.
    assert b"Updated Laptop" in response.data

def test_asset_approval(client, app):
    # Log in as admin.
    login(client, "admin1234", "1234")

    # Create an asset directly in the database for testing approval.
    asset = Asset(
        name="Test Device",
        category="Gadget",
        purchase_date=datetime.strptime("2025-06-13", "%Y-%m-%d").date(),
        status="Pending Approval",
        user_id=1,  # Assuming an admin user will have id=1.
    )
    with app.app_context():
        db.session.add(asset)
        db.session.commit()
        # Get the asset ID while the object is still bound.
        asset_id = asset.id

    # Approve the asset using its retrieved ID.
    response = client.post(f"/asset/approve/{asset_id}", follow_redirects=True)
    # After approval, the asset should now have status "Active" and be visible.
    assert b"Active" in response.data
    assert b"Test Device" in response.data

def test_asset_rejection(client, app):
    # Log in as admin.
    login(client, "admin1234", "1234")

    # Create another asset for testing rejection.
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

    # Reject the asset using its retrieved ID.
    response = client.post(f"/asset/reject/{asset_id}", follow_redirects=True)
    # After rejection, the asset should now have status "Rejected".
    assert b"Rejected" in response.data
    assert b"Faulty Device" in response.data
