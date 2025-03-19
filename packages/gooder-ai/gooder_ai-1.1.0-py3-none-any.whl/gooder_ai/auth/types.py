from typing import TypedDict


class AuthenticateParams(TypedDict):
    email: str
    password: str
    app_client_id: str
    identity_pool_id: str
    user_pool_id: str
