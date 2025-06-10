from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create a global SQLAlchemy instance (do not bind it to an app yet)
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = 'devkey123'  # Used for form security
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assets.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy with the app
    db.init_app(app)

    # Register the blueprint for our routes
    from .routes import main
    app.register_blueprint(main)

    # Create the database tables if they don't exist already
    with app.app_context():
        db.create_all()

    return app
