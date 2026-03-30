from urllib.parse import quote

import requests
from flask import current_app


class Auth0ManagementError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


def _base_url():
    return f"https://{current_app.config['AUTH0_DOMAIN']}"


def get_management_token():
    payload = {
        "grant_type": "client_credentials",
        "client_id": current_app.config["AUTH0_MGMT_CLIENT_ID"],
        "client_secret": current_app.config["AUTH0_MGMT_CLIENT_SECRET"],
        "audience": current_app.config["AUTH0_MGMT_AUDIENCE"],
    }
    response = requests.post(
        f"{_base_url()}/oauth/token",
        json=payload,
        timeout=current_app.config["AUTH0_TIMEOUT_SECONDS"],
    )
    if response.status_code >= 400:
        raise Auth0ManagementError(response.status_code, "No se pudo obtener token de Management API")
    return response.json().get("access_token")


def _request(method, path, token, **kwargs):
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {token}"
    headers["Content-Type"] = "application/json"

    response = requests.request(
        method,
        f"{_base_url()}{path}",
        headers=headers,
        timeout=current_app.config["AUTH0_TIMEOUT_SECONDS"],
        **kwargs,
    )

    if response.status_code >= 400:
        details = response.text
        try:
            details = response.json()
        except ValueError:
            pass
        raise Auth0ManagementError(response.status_code, f"Auth0 error: {details}")
    if response.text:
        return response.json()
    return None


def list_users(token):
    return _request("GET", "/api/v2/users?per_page=100&page=0&include_totals=false", token)


def get_user(token, user_id):
    return _request("GET", f"/api/v2/users/{quote(user_id, safe='')}", token)


def create_user(token, data):
    return _request("POST", "/api/v2/users", token, json=data)


def update_user(token, user_id, data):
    return _request("PATCH", f"/api/v2/users/{quote(user_id, safe='')}", token, json=data)


def delete_user(token, user_id):
    _request("DELETE", f"/api/v2/users/{quote(user_id, safe='')}", token)
