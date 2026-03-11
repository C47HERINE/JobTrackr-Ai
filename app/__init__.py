from flask import Flask
from .dashboard import dashboard_blueprints


def create_app(database):
    app = Flask(__name__)
    app.register_blueprint(dashboard_blueprints(database))
    return app