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
    db_fd, db_path = tempfile.mkstemp()
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "WTF_CSRF_ENABLED": False,
    }
    app = create_app(test_config)
    with app.app_context():
        if not User.query.filter_by(username="admin").first():
            admin_user = User(
                username="admin",
                password=generate_password_hash("Admin#12345", method="pbkdf2:sha256"),
                role="admin",
            )
            db.session.add(admin_user)
            db.session.commit()
    yield app
    with app.app_context():
        db.session.remove()
        db.engine.dispose()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
