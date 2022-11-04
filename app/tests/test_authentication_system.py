import base64
import json

import pytest
from app import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c

AUTH_TOKEN_ENDPOINT = "/auth/token/"

def test_username_dne(client):
    response = client.post(AUTH_TOKEN_ENDPOINT, data={
        "username": "dne@gmail.com",
        "password": "password123"
    })
    
    assert response.status_code == 401


def test_valid_username_with_invalid_password(client):
    response = client.post(AUTH_TOKEN_ENDPOINT, data={
        "username": "jeff.bezos@sjsu.edu",
        "password": "usersuper"
    })

    assert response.status_code == 401


def test_valid_username_with_valid_password(client):
    response = client.post(AUTH_TOKEN_ENDPOINT, data={
        "username": "jeff.bezos@sjsu.edu",
        "password": "superuser"
    })
    
    assert response.status_code == 200

    # decode auth token and test contents
    user = json.loads(base64.b64decode(response.json()["access_token"].split(".")[1] + '==').decode('utf-8'))
    assert 'password' not in user;
    assert user['email'] == 'jeff.bezos@sjsu.edu';
    assert user['is_superuser'] == True
