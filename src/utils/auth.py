import json
from functools import wraps
from urllib.request import urlopen

from flask import current_app, request
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code
        super().__init__(str(error))


def get_token_auth_header():
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError(
            {"code": "authorization_header_missing", "description": "Authorization header is expected"},
            401,
        )

    parts = auth.split()
    if parts[0].lower() != "bearer":
        raise AuthError(
            {"code": "invalid_header", "description": "Authorization header must start with Bearer"},
            401,
        )
    if len(parts) == 1:
        raise AuthError({"code": "invalid_header", "description": "Token not found"}, 401)
    if len(parts) > 2:
        raise AuthError({"code": "invalid_header", "description": "Malformed authorization header"}, 401)

    return parts[1]


def _get_rsa_key(token):
    domain = current_app.config["AUTH0_DOMAIN"]
    jsonurl = urlopen(f"https://{domain}/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)

    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            return {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
    return None


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        rsa_key = _get_rsa_key(token)

        if not rsa_key:
            raise AuthError({"code": "invalid_header", "description": "Unable to find appropriate key"}, 401)

        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=current_app.config["AUTH0_ALGORITHMS"],
                audience=current_app.config["AUTH0_AUDIENCE"],
                issuer=f"https://{current_app.config['AUTH0_DOMAIN']}/",
            )
        except ExpiredSignatureError as exc:
            raise AuthError({"code": "token_expired", "description": "Token expired"}, 401) from exc
        except JWTClaimsError as exc:
            raise AuthError({"code": "invalid_claims", "description": "Incorrect claims"}, 401) from exc
        except JWTError as exc:
            raise AuthError({"code": "invalid_token", "description": "Unable to parse token"}, 400) from exc

        return f(payload, *args, **kwargs)

    return decorated
