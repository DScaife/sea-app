from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY="devkey123",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_DATABASE_URI="sqlite:///assets.db",
    )

    if test_config is not None:
        app.config.from_mapping(test_config)

    db.init_app(app)

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
        if not User.query.filter_by(username="admin1234").first():
            admin_user = User(
                username="admin1234",
                password=generate_password_hash("1234", method="pbkdf2:sha256"),
                role="admin",
            )
            db.session.add(admin_user)
            db.session.commit()

    return app
