import secrets
from flask import Flask
from .dashboard import dashboard_blueprints
from flask_wtf.csrf import CSRFProtect


def create_app(database):
    app = Flask(__name__)
    app.register_blueprint(dashboard_blueprints(database))
    app.config['SECRET_KEY'] = secrets.token_urlsafe(32)
    CSRFProtect(app)
    return app