from httpx import AsyncClient

from .test_auth_routes import AUTH_TOKEN_ENDPOINT
from .test_category_routes import (GET_ALL_CATEGORY_ENDPOINT,
                                   GET_CATEGORY_BY_SLUG_ENDPOINT)

UPDATE_PRODUCT_ENDPOINT = '/product/{id}'
GET_PRODUCT_BY_SLUG_ENDPOINT = '/product/{slug}'
GET_CATEGORY_BY_SLUG_ENDPOINT_WITH_PRODUCTS = f'{GET_CATEGORY_BY_SLUG_ENDPOINT}?expand=products'

UPDATE_PRODUCT_QUANTITY = 100
UPDATE_PRODUCT_PRICE = 9.99

async def test_get_product_by_slug(client: AsyncClient):
    # get all categories
    response = await client.get(GET_ALL_CATEGORY_ENDPOINT)

    assert response.status_code == 200

    # get all products from the first category
    response = await client.get(
        GET_CATEGORY_BY_SLUG_ENDPOINT_WITH_PRODUCTS.format(
            slug=response.json()['items'][0]['slug']
        )
    )

    assert response.status_code == 200

    data = response.json()

    assert 'products' in data
    
    # get the first product from the first category
    response = await client.get(GET_PRODUCT_BY_SLUG_ENDPOINT.format(slug=data['products'][0]['slug']))

    assert response.status_code == 200

    data = response.json()

    assert 'id' in data
    assert 'category_id' in data
    assert 'slug' in data
    assert 'quantity' in data
    assert 'weight' in data
    assert 'name' in data
    assert 'image_url' in data
    assert 'description' in data
    assert 'price' in data

    
async def test_update_product_underprivileged(client: AsyncClient):
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        'username': 'morgan.freemen@sjsu.edu',
        'password': 'customer'
    })

    assert response.status_code == 200

    response = await client.patch(UPDATE_PRODUCT_ENDPOINT.format(id=5), 
        json={
            "quantity": UPDATE_PRODUCT_QUANTITY,
            "price": UPDATE_PRODUCT_PRICE
        }
    )

    assert response.status_code == 401

async def test_get_product_by_slug_dne(client: AsyncClient):
    # get all products from the first category
    response = await client.get(
        GET_PRODUCT_BY_SLUG_ENDPOINT.format(
            slug='does-not-exist'
        )
    )

    assert response.status_code == 404


async def test_update_product_privileged(client: AsyncClient):
    # get all categories
    response = await client.get(GET_ALL_CATEGORY_ENDPOINT)

    assert response.status_code == 200

    # get all products from the first category
    response = await client.get(
        GET_CATEGORY_BY_SLUG_ENDPOINT_WITH_PRODUCTS.format(
            slug=response.json()['items'][0]['slug']
        )
    )

    assert response.status_code == 200

    data = response.json()
    product = data['products'][0]

    UPDATE_PRODUCT_ID = product['id']
    UPDATE_PRODUCT_SLUG = product['slug']

    # verify the product isn't what we want

    assert product['quantity'] != UPDATE_PRODUCT_QUANTITY
    assert product['price'] != UPDATE_PRODUCT_PRICE

    # login as a employee
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        'username': 'amy.dyken@sjsu.edu',
        'password': 'employee'
    })

    assert response.status_code == 200

    # update the product
    response = await client.patch(UPDATE_PRODUCT_ENDPOINT.format(id=UPDATE_PRODUCT_ID), 
        json={
            "quantity": UPDATE_PRODUCT_QUANTITY,
            "price": UPDATE_PRODUCT_PRICE
        }
    )

    assert response.status_code == 200

    # verify the changes are reflected in the database
    response = await client.get(GET_PRODUCT_BY_SLUG_ENDPOINT.format(slug=UPDATE_PRODUCT_SLUG))

    assert response.status_code == 200

    data = response.json()

    assert data['quantity'] == UPDATE_PRODUCT_QUANTITY
    assert data['price'] == UPDATE_PRODUCT_PRICE



async def test_create_existing_category_privileged(client: AsyncClient):
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        'username': 'amy.dyken@sjsu.edu',
        'password': 'employee'
    })
    
    assert response.status_code == 200

    # update the nonexistant product
    response = await client.patch(UPDATE_PRODUCT_ENDPOINT.format(id=463786), 
        json={
            "quantity": UPDATE_PRODUCT_QUANTITY,
            "price": UPDATE_PRODUCT_PRICE
        }
    )

    assert response.status_code == 404
