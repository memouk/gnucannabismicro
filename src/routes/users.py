from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from src.extensions import db
from src.models.user import User
from src.utils.auth import requires_auth

users_bp = Blueprint("users", __name__)


def _normalize_user_payload(payload):
    # Soporte temporal para payload viejo (username/full_name/is_active).
    normalized = {
        "nombre": payload.get("nombre") or payload.get("full_name"),
        "email": payload.get("email"),
        "password_hash": payload.get("password_hash"),
        "activo": payload.get("activo", payload.get("is_active", True)),
    }
    return normalized


def _validate_payload(payload):
    required = ["nombre", "email", "password_hash"]
    missing = [field for field in required if not payload.get(field)]
    if missing:
        return f"Campos requeridos faltantes: {', '.join(missing)}"
    return None


@users_bp.get("/users")
@users_bp.get("/usuarios")
@requires_auth
def list_users(_jwt_payload):
    users = User.query.order_by(User.id.asc()).all()
    return jsonify([u.to_dict() for u in users]), 200


@users_bp.get("/users/<int:user_id>")
@users_bp.get("/usuarios/<int:user_id>")
@requires_auth
def get_user(_jwt_payload, user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(user.to_dict()), 200


@users_bp.post("/users")
@users_bp.post("/usuarios")
@requires_auth
def create_user(_jwt_payload):
    payload = _normalize_user_payload(request.get_json(silent=True) or {})
    error = _validate_payload(payload)
    if error:
        return jsonify({"error": error}), 400

    user = User(
        nombre=payload["nombre"],
        email=payload["email"],
        password_hash=payload["password_hash"],
        activo=payload.get("activo", True),
    )
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "email ya existe"}), 409

    return jsonify(user.to_dict()), 201


@users_bp.put("/users/<int:user_id>")
@users_bp.put("/usuarios/<int:user_id>")
@requires_auth
def update_user(_jwt_payload, user_id):
    payload = _normalize_user_payload(request.get_json(silent=True) or {})
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    user.nombre = payload.get("nombre", user.nombre)
    user.email = payload.get("email", user.email)
    user.password_hash = payload.get("password_hash", user.password_hash)
    user.activo = payload.get("activo", user.activo)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "email ya existe"}), 409

    return jsonify(user.to_dict()), 200


@users_bp.delete("/users/<int:user_id>")
@users_bp.delete("/usuarios/<int:user_id>")
@requires_auth
def delete_user(_jwt_payload, user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"deleted": True, "id": user_id}), 200
