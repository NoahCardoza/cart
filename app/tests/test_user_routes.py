from httpx import AsyncClient

from .test_auth_routes import AUTH_TOKEN_ENDPOINT

USER_ME_ENDPOINT = "/user/me/"

async def test_without_session(client: AsyncClient):
    """Test that the /user/me/ endpoint returns a 422 when no session cookie is provided."""

    response = await client.get(USER_ME_ENDPOINT)

    assert response.status_code == 422


async def test_with_invalid_session(client: AsyncClient):
    """Test that the /user/me/ endpoint returns a 401 when an invalid session cookie is provided."""

    response = await client.get(
        USER_ME_ENDPOINT,
        headers={
            'Cookie': 'session=invalid',
        }
    )

    assert response.status_code == 401

async def test_with_valid_session(client: AsyncClient):
    """Test that the /user/me/ endpoint returns a 200 when a valid session cookie is provided after logging in."""

    email = 'jeff.bezos@sjsu.edu'

    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        "username": email,
        "password": "superuser"
    })
    
    assert response.status_code == 200

    response = await client.get(USER_ME_ENDPOINT)

    assert response.status_code == 200
    
    data = response.json()

    assert data['email'] == email
    assert data['is_superuser'] == True
