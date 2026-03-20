import os

try:
    # Local execution from inside asset_manager/ (python run.py)
    from app import create_app
except ModuleNotFoundError:
    # Vercel imports from repository root
    from asset_manager.app import create_app

app = create_app()

if __name__ == '__main__':
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)
