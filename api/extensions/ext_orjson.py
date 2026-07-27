from flask_orjson import OrjsonProvider

from orqivium_app import OrqiviumApp


def init_app(app: OrqiviumApp):
    """Initialize Flask-Orjson extension for faster JSON serialization"""
    app.json = OrjsonProvider(app)
