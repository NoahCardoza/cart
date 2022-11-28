from httpx import AsyncClient

from .test_category_routes import (GET_ALL_CATEGORY_ENDPOINT,
                                   GET_CATEGORY_BY_SLUG_ENDPOINT)

GET_CATEGORY_BY_SLUG_ENDPOINT_WITH_PRODUCTS = f'{GET_CATEGORY_BY_SLUG_ENDPOINT}?expand=products'


async def test_field_expansion_valid(client: AsyncClient):
    """Test that the /category/{slug} endpoint returns a 200 when a valid slug is provided."""

    response = await client.get(
        GET_CATEGORY_BY_SLUG_ENDPOINT_WITH_PRODUCTS.format(slug='fruits')
    )

    assert response.status_code == 200

    data = response.json()

    assert 'products' in data


async def test_field_expansion_invalid(client: AsyncClient):
    """ Test that the /category/{slug} endpoint returns a 422 when an invalid field is provided in the expand query parameter. """

    response = await client.get(
        GET_CATEGORY_BY_SLUG_ENDPOINT_WITH_PRODUCTS.format(slug='fuits') + ',invalid_field'
    )

    assert response.status_code == 422
    assert response.json()[0]['type'] == 'value_error.expand.unknown'