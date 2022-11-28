from httpx import AsyncClient

from .test_auth_routes import AUTH_TOKEN_ENDPOINT

GET_ALL_CATEGORY_ENDPOINT = '/category/'
CREATE_CATEGORY_ENDPOINT = '/category/'
GET_CATEGORY_BY_SLUG_ENDPOINT = '/category/{slug}'

TEST_CATEGORY_NAME = 'Test Category'
TEST_CATEGORY_DESCRIPTION = 'Testing 123...'

async def test_get_all_categories(client: AsyncClient):
    response = await client.get(GET_ALL_CATEGORY_ENDPOINT)

    assert response.status_code == 200
    
    data = response.json()

    assert 'items' in data
    assert 'total' in data
    assert 'page' in data
    assert 'size' in data

    
async def test_get_category_by_slug(client: AsyncClient):
    response = await client.get(GET_ALL_CATEGORY_ENDPOINT)

    assert response.status_code == 200

    response = await client.get(GET_CATEGORY_BY_SLUG_ENDPOINT.format(slug=response.json()['items'][0]['slug']))

    assert response.status_code == 200

    data = response.json()

    assert 'image_url' in data
    assert 'name' in data
    assert 'description' in data
    assert 'id' in data
    assert 'slug' in data

async def test_get_category_by_slug_dne(client: AsyncClient):
    response = await client.get(GET_ALL_CATEGORY_ENDPOINT)

    assert response.status_code == 200

    response = await client.get(GET_CATEGORY_BY_SLUG_ENDPOINT.format(slug='does-not-exist'))

    assert response.status_code == 404


async def test_create_category_underprivileged(client: AsyncClient):
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        'username': 'morgan.freemen@sjsu.edu',
        'password': 'customer'
    })

    assert response.status_code == 200

    response = await client.post(CREATE_CATEGORY_ENDPOINT, json={
        'image_url': 'https://allthatsinteresting.com/wordpress/wp-content/uploads/2012/06/iconic-photos-1950-einstein.jpg',
        'name': TEST_CATEGORY_NAME,
        'description': TEST_CATEGORY_DESCRIPTION,
    })

    assert response.status_code == 401
    

async def test_create_category_privileged(client: AsyncClient):
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        'username': 'jeff.bezos@sjsu.edu',
        'password': 'superuser'
    })
    
    assert response.status_code == 200

    response = await client.post(CREATE_CATEGORY_ENDPOINT, json={
        'image_url': 'https://allthatsinteresting.com/wordpress/wp-content/uploads/2012/06/iconic-photos-1950-einstein.jpg',
        'name': TEST_CATEGORY_NAME,
        'description': TEST_CATEGORY_DESCRIPTION,
    })

    assert response.status_code == 200

    response = await client.get(GET_ALL_CATEGORY_ENDPOINT)

    assert response.status_code == 200
    
    assert TEST_CATEGORY_NAME in [item['name'] for item in response.json()['items']]    


async def test_create_existing_category_privileged(client: AsyncClient):
    response = await client.post(AUTH_TOKEN_ENDPOINT, data={
        'username': 'jeff.bezos@sjsu.edu',
        'password': 'superuser'
    })
    
    assert response.status_code == 200

    response = await client.post(CREATE_CATEGORY_ENDPOINT, json={
        'image_url': 'https://allthatsinteresting.com/wordpress/wp-content/uploads/2012/06/iconic-photos-1950-einstein.jpg',
        'name': 'Fruits',
        'description': TEST_CATEGORY_DESCRIPTION,
    })

    assert response.status_code == 409
