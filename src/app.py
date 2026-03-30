from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import text

from src.config import Config
from src.extensions import db, migrate
from src.routes.auth import auth_bp
from src.routes.health import health_bp
from src.routes.masters import masters_bp
from src.routes.users import users_bp
from src.routes.web_auth import web_auth_bp
from src.utils.auth import AuthError

load_dotenv()


def _sync_schema_for_estados():
    bootstrap = [
        """
        CREATE TABLE IF NOT EXISTS estados (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(50) NOT NULL UNIQUE,
            descripcion VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        INSERT INTO estados (nombre, descripcion)
        VALUES
            ('ACTIVO', 'Registro habilitado'),
            ('INACTIVO', 'Registro deshabilitado')
        ON DUPLICATE KEY UPDATE descripcion = VALUES(descripcion)
        """,
    ]
    for stmt in bootstrap:
        db.session.execute(text(stmt))

    col_check_sql = """
    SELECT COUNT(*) AS total
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = :table_name
      AND COLUMN_NAME = 'estado_id'
    """
    for table_name in ("cultivos", "plantas"):
        col_exists = db.session.execute(
            text(col_check_sql), {"table_name": table_name}
        ).scalar()
        if not col_exists:
            db.session.execute(
                text(f"ALTER TABLE {table_name} ADD COLUMN estado_id INT NULL AFTER estado")
            )

    fk_check_sql = """
    SELECT COUNT(*) AS total
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = :table_name
      AND COLUMN_NAME = 'estado_id'
      AND REFERENCED_TABLE_NAME = 'estados'
    """
    for table_name, constraint_name in (
        ("cultivos", "fk_cultivos_estado"),
        ("plantas", "fk_plantas_estado"),
    ):
        fk_exists = db.session.execute(
            text(fk_check_sql), {"table_name": table_name}
        ).scalar()
        if not fk_exists:
            db.session.execute(
                text(
                    f"ALTER TABLE {table_name} "
                    f"ADD CONSTRAINT {constraint_name} "
                    "FOREIGN KEY (estado_id) REFERENCES estados(id)"
                )
            )

    backfill = [
        """
        UPDATE cultivos c
        JOIN estados e ON UPPER(TRIM(c.estado)) = e.nombre
        SET c.estado_id = e.id
        WHERE c.estado_id IS NULL AND c.estado IS NOT NULL AND c.estado <> ''
        """,
        """
        UPDATE plantas p
        JOIN estados e ON UPPER(TRIM(p.estado)) = e.nombre
        SET p.estado_id = e.id
        WHERE p.estado_id IS NULL AND p.estado IS NOT NULL AND p.estado <> ''
        """,
    ]
    for stmt in backfill:
        db.session.execute(text(stmt))
    db.session.commit()


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
        from src.models.estado import Estado  # noqa: F401
        from src.models.insumo import Insumo  # noqa: F401
        from src.models.lote import Lote  # noqa: F401
        from src.models.planta import Planta  # noqa: F401
        from src.models.proveedor import Proveedor  # noqa: F401
        from src.models.user import User  # noqa: F401

        db.create_all()
        _sync_schema_for_estados()

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000)
