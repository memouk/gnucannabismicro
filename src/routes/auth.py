from flask import Blueprint, jsonify

from src.utils.auth import requires_auth

auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/me")
@requires_auth
def me(payload):
    return jsonify({"user": payload}), 200
