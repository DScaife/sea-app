import os
import secrets
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from werkzeug.security import generate_password_hash
from sqlalchemy import inspect, text
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

db = SQLAlchemy()
csrf = CSRFProtect()


def _migrate_user_table_if_needed():
    """Lightweight migration for existing SQLite DBs without Alembic."""
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()
    if "user" not in table_names:
        return

    existing_columns = {col["name"] for col in inspector.get_columns("user")}

    if "failed_login_attempts" not in existing_columns:
        db.session.execute(
            text(
                "ALTER TABLE user ADD COLUMN failed_login_attempts INTEGER NOT NULL DEFAULT 0"
            )
        )

    if "locked_until" not in existing_columns:
        db.session.execute(text("ALTER TABLE user ADD COLUMN locked_until DATETIME"))

    db.session.commit()


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", secrets.token_hex(32)),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///assets.db"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("SESSION_COOKIE_SECURE", "false").lower()
        == "true",
        REMEMBER_COOKIE_HTTPONLY=True,
    )

    if test_config is not None:
        app.config.from_mapping(test_config)

    db.init_app(app)
    csrf.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from .routes import main

    app.register_blueprint(main)

    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    with app.app_context():
        db.create_all()
        _migrate_user_table_if_needed()

        bootstrap_admin_username = os.getenv("BOOTSTRAP_ADMIN_USERNAME")
        bootstrap_admin_password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD")

        if (
            bootstrap_admin_username
            and bootstrap_admin_password
            and not User.query.filter_by(username=bootstrap_admin_username).first()
        ):
            admin_user = User(
                username=bootstrap_admin_username,
                password=generate_password_hash(
                    bootstrap_admin_password, method="pbkdf2:sha256"
                ),
                role="admin",
            )
            db.session.add(admin_user)
            db.session.commit()

    return app
