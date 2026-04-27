"""ACEest Fitness & Gym - Flask application package.

Version 1.0 - Programs catalog (mirrors Aceestver-1.0.py).
Future versions will add: clients, persistence, progress, auth, reports.
"""
from flask import Flask

from .programs import PROGRAMS
from .routes import register_routes

__version__ = "1.0.0"


def create_app() -> Flask:
    """Application factory used by the entry point and tests."""
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    app.config["VERSION"] = __version__
    app.config["PROGRAMS"] = PROGRAMS
    register_routes(app)
    return app
