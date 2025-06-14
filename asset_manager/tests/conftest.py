import os
import tempfile
import pytest
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import create_app, db
from app.models import User, Asset
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    # Create a temporary file to act as the test database.
    db_fd, db_path = tempfile.mkstemp()
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "WTF_CSRF_ENABLED": False,
    }
    app = create_app(test_config)
    yield app
    # Teardown cleanup: remove sessions and dispose of the engine.
    with app.app_context():
        db.session.remove()  # Remove any active sessions
        db.engine.dispose()  # Dispose of the engine (closes connections)
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
