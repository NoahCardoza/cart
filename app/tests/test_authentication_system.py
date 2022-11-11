import base64
import json

from httpx import AsyncClient

AUTH_TOKEN_ENDPOINT = "/auth/token/"


def decode_auth_token(auth_token):
    return json.loads(base64.b64decode(auth_token.split(".")[1] + '==').decode('utf-8'))


async def test_username_dne(client: AsyncClient):
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        "username": "dne@gmail.com",
        "password": "password123"
    })

    assert response.status_code == 401


async def test_valid_username_with_invalid_password(client):
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        "username": "jeff.bezos@sjsu.edu",
        "password": "usersuper"
    })

    assert response.status_code == 401


async def test_valid_superuser_login(client):
    email = 'jeff.bezos@sjsu.edu'

    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        "username": email,
        "password": "superuser"
    })
    
    assert response.status_code == 200

    # decode auth token and test contents
    user = decode_auth_token(response.json()["access_token"])
    assert 'password' not in user;
    assert user['email'] == email;
    assert user['is_superuser'] == True


async def test_valid_employee_login(client):
    email = "amy.dyken@sjsu.edu"

    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        "username": email,
        "password": "employee"
    })
    
    assert response.status_code == 200

    # decode auth token and test contents
    user = decode_auth_token(response.json()["access_token"])
    assert 'password' not in user;
    assert user['email'] == email;
    assert user['is_employee'] == True


async def test_valid_customer_login(client):
    email = "morgan.freemen@sjsu.edu"

    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        "username": email,
        "password": "customer"
    })
    
    assert response.status_code == 200

    # decode auth token and test contents
    user = decode_auth_token(response.json()["access_token"])
    assert 'password' not in user;
    assert user['email'] == email;
    assert not user['is_superuser']
    assert not user['is_employee']
