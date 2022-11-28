from httpx import AsyncClient

from .test_auth_routes import AUTH_TOKEN_ENDPOINT
from .test_category_routes import (GET_ALL_CATEGORY_ENDPOINT,
                                   GET_CATEGORY_BY_SLUG_ENDPOINT)

GET_CART_ENDPOINT = '/cart/'
GET_CART_CHECKOUT = '/cart/checkout/'
UPDATE_CART_ENDPOINT = '/cart/{id}'


async def test_get_cart_unauthenticated(client: AsyncClient):
    response = await client.get(
        GET_CART_ENDPOINT, 
        headers={
            'Cookie': 'session=invalid',
        }
    )

    assert response.status_code == 401

async def test_add_to_cart_unauthenticated(client: AsyncClient):
    response = await client.post(
        GET_CART_ENDPOINT, 
        headers={
            'Cookie': 'session=invalid',
        },
        json={
            'product_id': 1,
            'quantity': 1
        }
    )

    assert response.status_code == 401
    

async def test_get_cart(client: AsyncClient):
    # login
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        'username': 'morgan.freemen@sjsu.edu',
        'password': 'customer'
    })

    assert response.status_code == 200

    response = await client.get(GET_CART_ENDPOINT)

    assert response.status_code == 200

    data = response.json()

    assert 'id' in data
    assert 'created_at' in data
    assert 'updated_at' in data
    assert 'items' in data

    
async def test_add_to_cart_and_delete(client: AsyncClient):
     # login
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        'username': 'morgan.freemen@sjsu.edu',
        'password': 'customer'
    })

    assert response.status_code == 200

    response = await client.post(
        GET_CART_ENDPOINT, 
        json={
            'product_id': 1,
            'quantity': 1
        }
    )

    assert response.status_code == 200
    
    # test adding after already being added
    response = await client.post(
        GET_CART_ENDPOINT, 
        json={
            'product_id': 1,
            'quantity': 1
        }
    )

    assert response.status_code == 200

    response = await client.delete(UPDATE_CART_ENDPOINT.format(id=response.json()['id']))

    assert response.status_code == 204

    
async def test_delete_cart_item_dne(client: AsyncClient):
     # login
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        'username': 'morgan.freemen@sjsu.edu',
        'password': 'customer'
    })

    assert response.status_code == 200

    response = await client.delete(UPDATE_CART_ENDPOINT.format(id=1337))

    assert response.status_code == 404

    
async def test_add_to_cart_not_enough_stock(client: AsyncClient):
     # login
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        'username': 'morgan.freemen@sjsu.edu',
        'password': 'customer'
    })

    assert response.status_code == 200

    response = await client.post(
        GET_CART_ENDPOINT, 
        json={
            'product_id': 3,
            'quantity': 1000
        }
    )

    assert response.status_code == 400

    
async def test_update_cart_item_dne(client: AsyncClient):
     # login
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        'username': 'morgan.freemen@sjsu.edu',
        'password': 'customer'
    })

    assert response.status_code == 200

    response = await client.patch(
        UPDATE_CART_ENDPOINT.format(id=4673), 
        json={
            'quantity': 5
        }
    )

    assert response.status_code == 404

async def test_update_cart_item_and_delete(client: AsyncClient):
     # login
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        'username': 'morgan.freemen@sjsu.edu',
        'password': 'customer'
    })

    PRODUCT_ID = 5

    assert response.status_code == 200

    response = await client.post(
        GET_CART_ENDPOINT, 
        json={
            'product_id': PRODUCT_ID,
            'quantity': 1
        }
    )

    assert response.status_code == 200

    ORDER_ITEM_ID = response.json()['id']

    response = await client.patch(
        UPDATE_CART_ENDPOINT.format(id=ORDER_ITEM_ID), 
        json={
            'quantity': 5
        }
    )

    assert response.status_code == 200

    response = await client.patch(
        UPDATE_CART_ENDPOINT.format(id=ORDER_ITEM_ID), 
        json={
            'quantity': 500
        }
    )

    assert response.status_code == 400

    response = await client.delete(UPDATE_CART_ENDPOINT.format(id=ORDER_ITEM_ID))

    assert response.status_code == 204

async def test_checkout_under_20lbs(client: AsyncClient):
     # login
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        'username': 'morgan.freemen@sjsu.edu',
        'password': 'customer'
    })

    assert response.status_code == 200

    response = await client.post(
        GET_CART_ENDPOINT, 
        json={
            'product_id': 11,
            'quantity': 1
        }
    )

    assert response.status_code == 200
    # for i in range(1, 10):
    #     response = await client.post(
    #         GET_CART_ENDPOINT, 
    #         json={
    #             'product_id': i,
    #             'quantity': 10
    #         }
    #     )

    #     assert response.status_code == 200
    
    response = await client.post(GET_CART_CHECKOUT)
    
    assert response.status_code == 200

    print('\nunder:', response.json()['url'])

async def test_checkout_over_20lbs(client: AsyncClient):
     # login
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        'username': 'morgan.freemen@sjsu.edu',
        'password': 'customer'
    })

    assert response.status_code == 200

    for i in range(1, 10):
        response = await client.post(
            GET_CART_ENDPOINT, 
            json={
                'product_id': i,
                'quantity': 10
            }
        )

        assert response.status_code == 200
    
    response = await client.post(GET_CART_CHECKOUT)
    
    assert response.status_code == 200

    print('\nover:', response.json()['url'])