import base64
import json

from httpx import AsyncClient

AUTH_TOKEN_ENDPOINT = "/auth/token/"
AUTH_REGISTER_ENDPOINT = "/auth/register"


def decode_auth_token(auth_token: str) -> dict:
    return json.loads(base64.b64decode(auth_token.split(".")[1] + '==').decode('utf-8'))


async def test_username_dne(client: AsyncClient):
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        "username": "dne@gmail.com",
        "password": "password123"
    })

    assert response.status_code == 401


async def test_valid_username_with_invalid_password(client: AsyncClient):
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        "username": "jeff.bezos@sjsu.edu",
        "password": "usersuper"
    })

    assert response.status_code == 401
    assert response.json()['detail'] == 'Incorrect username or password'


async def test_valid_superuser_login(client: AsyncClient):
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


async def test_valid_employee_login(client: AsyncClient):
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


async def test_valid_customer_login(client: AsyncClient):
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


async def test_register_new_user_short_password(client: AsyncClient):
    email = "john.malkovich@sjsu.edu"
    password = "TAsqf"

    response = await client.post(AUTH_REGISTER_ENDPOINT, json={
        "firstname": "John",
        "lastname": "Malkovich",
        "username": email,
        "password": password,
    })
    
    assert response.status_code == 422

    data = response.json()[0]
    assert data['loc'] == ['body', 'password']
    

async def test_register_new_user_long_password(client):
    email = "jim.carrey@sjsu.edu"
    password = "4f79ce357d3173545055e5a33a710cec4f79ce357d3173545055e5a33a710cec"

    response = await client.post(AUTH_REGISTER_ENDPOINT, json={
        "firstname": "Jim",
        "lastname": "Carrey",
        "username": email,
        "password": password,
    })
    
    assert response.status_code == 422
    
    data = response.json()[0]
    assert data['loc'] == ['body', 'password']


async def test_register_new_user_and_login(client):
    email = "emma.stone@sjsu.edu"
    password = "4f79ce357d3173545055e5a33a710cec"

    response = await client.post(AUTH_REGISTER_ENDPOINT, json={
        "firstname": "Emma",
        "lastname": "Stone",
        "username": email,
        "password": password,
    })
    
    assert response.status_code == 200
    
    data = response.json()
    assert 'access_token' in data

    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        "username": email,
        "password": password
    })
    
    data = response.json()

    assert response.status_code == 200
    assert 'access_token' in data


async def test_register_new_user_with_duplicate_email(client):
    response = await client.post(AUTH_REGISTER_ENDPOINT, json={
        "firstname": "Morganna",
        "lastname": "Freewoman",
        "username": "morgan.freemen@sjsu.edu",
        "password": "ce7860b44604696b24e2",
    })

    assert response.status_code == 409
