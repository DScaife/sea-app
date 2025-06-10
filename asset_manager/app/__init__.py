from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

# Create a global SQLAlchemy instance (do not bind it to an app yet)
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = 'devkey123'  # For securing sessions and forms
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assets.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy with the app
    db.init_app(app)
    
    # Set up Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Where unauthorized users are redirected
    login_manager.init_app(app)
    
    # (We'll define a user loader in a moment; see the User model below)
    from .models import User  # Ensure the User model is imported so that the loader finds it

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints:
    from .routes import main
    app.register_blueprint(main)
    
    # Register the authentication blueprint (we'll create auth.py next)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    # Create the database tables if they don't exist already
    with app.app_context():
        db.create_all()
        # Seed a default admin account if one doesn't exist
        if not User.query.filter_by(username='admin1234').first():
            admin_user = User(
                username='admin1234',
                email='admin@example.com',
                password=generate_password_hash('1234', method='pbkdf2:sha256'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()

    return app
