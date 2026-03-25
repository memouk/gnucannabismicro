from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from src.config import Config
from src.extensions import db, migrate
from src.routes.auth import auth_bp
from src.routes.health import health_bp
from src.routes.masters import masters_bp
from src.routes.users import users_bp
from src.routes.web_auth import web_auth_bp
from src.utils.auth import AuthError

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = app.config["AUTH0_SECRET"]
    CORS(app)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(users_bp, url_prefix="/api")
    app.register_blueprint(masters_bp, url_prefix="/api")
    app.register_blueprint(web_auth_bp)

    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        return jsonify(ex.error), ex.status_code

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(400)
    def bad_request(_):
        return jsonify({"error": "Solicitud invalida"}), 400

    @app.errorhandler(500)
    def internal_error(_):
        return jsonify({"error": "Error interno del servidor"}), 500

    # Crea tablas mapeadas (incluye usuarios) si no existen.
    with app.app_context():
        from src.models.cultivo import Cultivo  # noqa: F401
        from src.models.insumo import Insumo  # noqa: F401
        from src.models.planta import Planta  # noqa: F401
        from src.models.user import User  # noqa: F401

        db.create_all()

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000)
