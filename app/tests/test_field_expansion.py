from httpx import AsyncClient

from .test_category_routes import GET_CATEGORY_BY_SLUG_ENDPOINT
from .test_product_routes import GET_PRODUCT_BY_SLUG_ENDPOINT

GET_CATEGORY_BY_SLUG_ENDPOINT_WITH_PRODUCTS = f'{GET_CATEGORY_BY_SLUG_ENDPOINT}?expand=products'
GET_PRODUCT_BY_SLUG_ENDPOINT_WITH_CATEGORY = f'{GET_PRODUCT_BY_SLUG_ENDPOINT}?expand=category'
GET_SEARCH_ENDPOINT_WITH_CATEGORY = '/search/?q={query}&expand=category'



async def test_field_expansion_valid_search(client: AsyncClient):
    """Test that the /category/{slug} endpoint returns a 200 when a valid expansion is provided."""

    response = await client.get(
        GET_SEARCH_ENDPOINT_WITH_CATEGORY.format(query='farm')
    )

    assert response.status_code == 200

    data = response.json()

    assert 'category' in data['items'][0]

async def test_field_expansion_valid_category(client: AsyncClient):
    """Test that the /category/{slug} endpoint returns a 200 when a valid expansion is provided."""

    response = await client.get(
        GET_CATEGORY_BY_SLUG_ENDPOINT_WITH_PRODUCTS.format(slug='fruits')
    )

    assert response.status_code == 200

    data = response.json()

    assert 'products' in data

async def test_field_expansion_valid_product(client: AsyncClient):
    """Test that the /prduct/{slug} endpoint returns a 200 when a valid expansion is provided."""

    response = await client.get(
        GET_PRODUCT_BY_SLUG_ENDPOINT_WITH_CATEGORY.format(slug='oranges')
    )

    assert response.status_code == 200

    data = response.json()

    assert 'category' in data


async def test_field_expansion_invalid(client: AsyncClient):
    """ Test that the /category/{slug} endpoint returns a 422 when an invalid field is provided in the expand query parameter. """

    response = await client.get(
        GET_CATEGORY_BY_SLUG_ENDPOINT_WITH_PRODUCTS.format(slug='fuits') + ',invalid_field'
    )

    assert response.status_code == 422
    assert response.json()[0]['type'] == 'value_error.expand.unknown'