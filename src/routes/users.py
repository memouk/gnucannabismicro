from flask import Blueprint, current_app, jsonify, request
from src.utils.auth0_management import (
    Auth0ManagementError,
    create_user as auth0_create_user,
    delete_user as auth0_delete_user,
    get_management_token,
    get_user as auth0_get_user,
    list_users as auth0_list_users,
    update_user as auth0_update_user,
)
from src.utils.auth import requires_auth

users_bp = Blueprint("users", __name__)


def _normalize_user_payload(payload):
    normalized = {
        "nombre": payload.get("nombre") or payload.get("full_name") or payload.get("name"),
        "email": payload.get("email"),
        "password": payload.get("password") or payload.get("password_hash"),
        "activo": payload.get("activo", payload.get("is_active", True)),
        "tipo_documento": payload.get("tipo_documento"),
        "numero_documento": payload.get("numero_documento"),
    }
    return normalized


def _validate_create_payload(payload):
    required = ["nombre", "email", "password"]
    missing = [field for field in required if not payload.get(field)]
    if missing:
        return f"Campos requeridos faltantes: {', '.join(missing)}"
    return None


@users_bp.get("/usuarios")
@requires_auth
def list_users(_jwt_payload):
    try:
        mgmt_token = get_management_token()
        users = auth0_list_users(mgmt_token)
        data = [
            {
                "id": u.get("user_id"),
                "nombre": u.get("name"),
                "email": u.get("email"),
                "activo": not bool(u.get("blocked", False)),
                "created_at": u.get("created_at"),
                "user_metadata": u.get("user_metadata") or {},
            }
            for u in users
        ]
        return jsonify(data), 200
    except Auth0ManagementError as exc:
        return jsonify({"error": exc.message}), exc.status_code


@users_bp.get("/usuarios/<path:user_id>")
@requires_auth
def get_user(_jwt_payload, user_id):
    try:
        mgmt_token = get_management_token()
        user = auth0_get_user(mgmt_token, user_id)
        return (
            jsonify(
                {
                    "id": user.get("user_id"),
                    "nombre": user.get("name"),
                    "email": user.get("email"),
                    "activo": not bool(user.get("blocked", False)),
                    "created_at": user.get("created_at"),
                    "user_metadata": user.get("user_metadata") or {},
                }
            ),
            200,
        )
    except Auth0ManagementError as exc:
        return jsonify({"error": exc.message}), exc.status_code


@users_bp.post("/usuarios")
@requires_auth
def create_user(_jwt_payload):
    payload = _normalize_user_payload(request.get_json(silent=True) or {})
    error = _validate_create_payload(payload)
    if error:
        return jsonify({"error": error}), 400

    try:
        mgmt_token = get_management_token()
        auth0_payload = {
            "connection": current_app.config["AUTH0_DB_CONNECTION"],
            "email": payload["email"],
            "password": payload["password"],
            "name": payload["nombre"],
            "blocked": not bool(payload.get("activo", True)),
            "email_verified": False,
            "verify_email": False,
            "user_metadata": {
                "tipo_documento": payload.get("tipo_documento"),
                "numero_documento": payload.get("numero_documento"),
            },
        }
        created = auth0_create_user(mgmt_token, auth0_payload)
        return (
            jsonify(
                {
                    "id": created.get("user_id"),
                    "nombre": created.get("name"),
                    "email": created.get("email"),
                    "activo": not bool(created.get("blocked", False)),
                    "created_at": created.get("created_at"),
                    "user_metadata": created.get("user_metadata") or {},
                }
            ),
            201,
        )
    except Auth0ManagementError as exc:
        return jsonify({"error": exc.message}), exc.status_code


@users_bp.put("/usuarios/<path:user_id>")
@requires_auth
def update_user(_jwt_payload, user_id):
    payload = _normalize_user_payload(request.get_json(silent=True) or {})
    try:
        mgmt_token = get_management_token()
        auth0_payload = {}
        if payload.get("nombre") is not None:
            auth0_payload["name"] = payload["nombre"]
        if payload.get("email") is not None:
            auth0_payload["email"] = payload["email"]
        if payload.get("password") is not None:
            auth0_payload["password"] = payload["password"]
        if payload.get("activo") is not None:
            auth0_payload["blocked"] = not bool(payload["activo"])

        if payload.get("tipo_documento") is not None or payload.get("numero_documento") is not None:
            auth0_payload["user_metadata"] = {
                "tipo_documento": payload.get("tipo_documento"),
                "numero_documento": payload.get("numero_documento"),
            }

        updated = auth0_update_user(mgmt_token, user_id, auth0_payload)
        return (
            jsonify(
                {
                    "id": updated.get("user_id"),
                    "nombre": updated.get("name"),
                    "email": updated.get("email"),
                    "activo": not bool(updated.get("blocked", False)),
                    "created_at": updated.get("created_at"),
                    "user_metadata": updated.get("user_metadata") or {},
                }
            ),
            200,
        )
    except Auth0ManagementError as exc:
        return jsonify({"error": exc.message}), exc.status_code


@users_bp.delete("/usuarios/<path:user_id>")
@requires_auth
def delete_user(_jwt_payload, user_id):
    try:
        mgmt_token = get_management_token()
        auth0_delete_user(mgmt_token, user_id)
        return jsonify({"deleted": True, "id": user_id}), 200
    except Auth0ManagementError as exc:
        return jsonify({"error": exc.message}), exc.status_code
