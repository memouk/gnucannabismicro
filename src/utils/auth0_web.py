import os

from auth0_server_python.auth_server.server_client import ServerClient
from dotenv import load_dotenv

load_dotenv()


class MemoryStateStore:
    """Almacen en memoria para desarrollo local."""

    def __init__(self):
        self._data = {}

    async def get(self, key, options=None):
        return self._data.get(key)

    async def set(self, key, value, options=None):
        self._data[key] = value

    async def delete(self, key, options=None):
        self._data.pop(key, None)

    async def delete_by_logout_token(self, claims, options=None):
        _ = claims
        return None


class MemoryTransactionStore:
    """Almacen de transacciones OAuth en memoria para desarrollo."""

    def __init__(self):
        self._data = {}

    async def get(self, key, options=None):
        return self._data.get(key)

    async def set(self, key, value, options=None):
        self._data[key] = value

    async def delete(self, key, options=None):
        self._data.pop(key, None)


state_store = MemoryStateStore()
transaction_store = MemoryTransactionStore()
authorization_params = {"scope": "openid profile email"}

audience = os.getenv("AUTH0_AUDIENCE", "").strip()
if audience:
    authorization_params["audience"] = audience

auth0 = ServerClient(
    domain=os.getenv("AUTH0_DOMAIN"),
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    secret=os.getenv("AUTH0_SECRET"),
    redirect_uri=os.getenv("AUTH0_REDIRECT_URI", "http://localhost:5000/callback"),
    state_store=state_store,
    transaction_store=transaction_store,
    authorization_params=authorization_params,
)
