from httpx import AsyncClient

from .test_auth_routes import AUTH_TOKEN_ENDPOINT
from .test_category_routes import (GET_ALL_CATEGORY_ENDPOINT,
                                   GET_CATEGORY_BY_SLUG_ENDPOINT)

GET_ORDERS_ENDPOINT = '/order/'
GET_ORDER_ENDPOINT = '/order/{id}/'


async def test_get_past_orders(client: AsyncClient):
    # login
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        'username': 'morgan.freemen@sjsu.edu',
        'password': 'customer'
    })

    assert response.status_code == 200

    response = await client.get(GET_ORDERS_ENDPOINT)

    assert response.status_code == 200

    
async def test_get_past_order(client: AsyncClient):
    # login
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        'username': 'morgan.freemen@sjsu.edu',
        'password': 'customer'
    })

    assert response.status_code == 200

    response = await client.get(GET_ORDER_ENDPOINT.format(id=1))

    assert response.status_code == 200


async def test_get_past_order_dne(client: AsyncClient):
    # login
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        'username': 'morgan.freemen@sjsu.edu',
        'password': 'customer'
    })

    assert response.status_code == 200

    response = await client.get(GET_ORDER_ENDPOINT.format(id=314))

    assert response.status_code == 404