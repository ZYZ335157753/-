from flask import Flask
from flask_cors import CORS

from config import Config
from routes.admin import admin_bp
from routes.api import api_bp
from services.store import ensure_database


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    app.config["DATABASE"].parent.mkdir(parents=True, exist_ok=True)
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    ensure_database(app.config["DATABASE"])

    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

