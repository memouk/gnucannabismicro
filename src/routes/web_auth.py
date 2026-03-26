from flask import Blueprint, current_app, g, jsonify, redirect, render_template, request, url_for
from auth0_server_python.auth_types import LogoutOptions
from urllib.parse import urlencode

from src.utils.auth0_web import auth0

web_auth_bp = Blueprint("web_auth", __name__)


@web_auth_bp.before_app_request
def store_request_context():
    g.store_options = {"request": request}


@web_auth_bp.get("/")
async def index():
    user = await auth0.get_user(g.store_options)
    return render_template("index.html", user=user)


@web_auth_bp.get("/login")
async def login():
    authorization_url = await auth0.start_interactive_login({}, g.store_options)
    return redirect(authorization_url)


@web_auth_bp.get("/callback")
async def callback():
    frontend_url = current_app.config["FRONTEND_URL"]
    error = request.args.get("error")
    description = request.args.get("error_description")

    if error:
        params = urlencode(
            {
                "auth_error": error,
                "auth_error_description": description or "Autenticacion cancelada o rechazada.",
            }
        )
        return redirect(f"{frontend_url}/?{params}")

    try:
        await auth0.complete_interactive_login(str(request.url), g.store_options)
        return redirect(frontend_url)
    except Exception as exc:  # noqa: BLE001
        params = urlencode(
            {
                "auth_error": "callback_failure",
                "auth_error_description": str(exc),
            }
        )
        return redirect(f"{frontend_url}/?{params}")


@web_auth_bp.get("/profile")
async def profile():
    user = await auth0.get_user(g.store_options)
    if not user:
        return redirect(url_for("web_auth.login"))
    return render_template("profile.html", user=user)


@web_auth_bp.get("/logout")
async def logout():
    return_to = current_app.config["BACKEND_LOGIN_URL"]
    try:
        logout_url = await auth0.logout(LogoutOptions(return_to=return_to), g.store_options)
        return redirect(logout_url)
    except Exception:  # noqa: BLE001
        return redirect(return_to)


@web_auth_bp.get("/auth/session")
async def session_data():
    user = await auth0.get_user(g.store_options)
    if not user:
        return jsonify({"authenticated": False}), 401

    token = None
    audience = current_app.config.get("AUTH0_AUDIENCE", "").strip()
    if audience:
        try:
            token = await auth0.get_access_token(g.store_options, audience=audience)
        except Exception:  # noqa: BLE001
            token = None

    return jsonify({"authenticated": True, "user": user, "access_token": token}), 200
