from flask import Blueprint, g, redirect, render_template, request, url_for
from auth0_server_python.auth_types import LogoutOptions

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
    try:
        await auth0.complete_interactive_login(str(request.url), g.store_options)
        return redirect(url_for("web_auth.profile"))
    except Exception as exc:  # noqa: BLE001
        return f"Error de autenticacion: {exc}", 400


@web_auth_bp.get("/profile")
async def profile():
    user = await auth0.get_user(g.store_options)
    if not user:
        return redirect(url_for("web_auth.login"))
    return render_template("profile.html", user=user)


@web_auth_bp.get("/logout")
async def logout():
    return_to = url_for("web_auth.index", _external=True)
    try:
        logout_url = await auth0.logout(LogoutOptions(return_to=return_to), g.store_options)
        return redirect(logout_url)
    except Exception:  # noqa: BLE001
        return redirect(return_to)
