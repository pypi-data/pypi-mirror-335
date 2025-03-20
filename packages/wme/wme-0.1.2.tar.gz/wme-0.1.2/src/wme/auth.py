from pydantic import BaseModel

import httpx

LOGIN_URL_PREFIX = "https://auth.enterprise.wikimedia.com/v1/login"
REFRESH_URL_PREFIX = "https://auth.enterprise.wikimedia.com/v1/token-refresh"
REVOKE_URL_PREFIX = "https://auth.enterprise.wikimedia.com/v1/token-revoke"

DEV_LOGIN_URL_PREFIX = "https://auth-dv.wikipediaenterprise.org/v1/login"
DEV_REFRESH_URL_PREFIX = "https://auth-dv.wikipediaenterprise.org/v1/token-refresh"
DEV_REVOKE_URL_PREFIX = "https://auth-dv.wikipediaenterprise.org/v1/token-revoke"


class TokenResponse(BaseModel):
    id_token: str
    access_token: str
    expires_in: int


class InitialTokenResponse(TokenResponse):
    challenge_name: str | None = None
    id_token: str
    access_token: str
    refresh_token: str
    session: str | None = None
    expires_in: int


async def login(
    username, password, client: httpx.AsyncClient | None = None
) -> InitialTokenResponse:
    client = client or httpx.AsyncClient()
    body = {"username": username, "password": password}
    response = await client.post(LOGIN_URL_PREFIX, json=body)
    response.raise_for_status()
    return InitialTokenResponse(**response.json())


async def refresh_token(
    username, refresh_token, client: httpx.AsyncClient | None = None
) -> TokenResponse:
    client = client or httpx.AsyncClient()
    body = {"username": username, "refresh_token": refresh_token}
    response = await client.post(REFRESH_URL_PREFIX, json=body)
    response.raise_for_status()
    return TokenResponse(**response.json())


async def revoke_token(refresh_token, client: httpx.AsyncClient | None = None) -> None:
    client = client or httpx.AsyncClient()
    body = {"refresh_token": refresh_token}
    response = await client.post(REVOKE_URL_PREFIX, json=body)
    response.raise_for_status()
    return None
