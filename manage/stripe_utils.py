from typing import Optional

import stripe
from app.stripe_config import (StripeShippingRateError, load_shipping_rates,
                               shipping_rates)
from typer import Option, Typer

stripe_app = Typer(
    help="A collection of commands to help with Stripe.")

shipping_options = [
    {
        "display_name": "Express",
        "delivery_estimate": {
        "maximum": {
            "unit": "hour",
            "value": 2
        },
        "minimum": {
            "unit": "hour",
            "value": 1
        }
        },
        "fixed_amount": {
            "amount": 1199,
            "currency": "usd"
        },
        "metadata": {
            "type": "express"
        },
        "tax_behavior": "exclusive",
        "type": "fixed_amount"
    },
    {
        "display_name": "Standard",
        "delivery_estimate": {
        "maximum": {
            "unit": "hour",
            "value": 4
        },
        "minimum": {
            "unit": "hour",
            "value": 2
        }
        },
        "fixed_amount": {
            "amount": 599,
            "currency": "usd"
        },
        "metadata": {
            "type": "standard"
        },
        "tax_behavior": "exclusive",
        "type": "fixed_amount"
    },
    {
        "display_name": "Complimentary",
        "delivery_estimate": {
        "maximum": {
            "unit": "hour",
            "value": 4
        },
        "minimum": {
            "unit": "hour",
            "value": 1
        }
        },
        "fixed_amount": {
            "amount": 0,
            "currency": "usd"
        },
        "metadata": {
            "type": "complimentary"
        },
        "tax_behavior": "exclusive",
        "type": "fixed_amount"
    }
]


@stripe_app.command()
def setup(
    api_key: Optional[str] = Option(
        None, 
        help="Use to configure on another Stripe Account, in production for example."
    ),
):
    """Create all necessary Stripe objects."""

    if api_key is not None:
        stripe.api_key = api_key

    try:
        load_shipping_rates()
        print('Shipping options already loaded.')
    except StripeShippingRateError:
        for shipping_option in shipping_options:
            shipping_type = shipping_option['metadata']['type']
            if shipping_rates[shipping_type] is None:
                shipping_rates[shipping_type] = stripe.ShippingRate.create(**shipping_option)
                print(f"Created shipping option: {shipping_type}")              
        print('Shipping options loaded.')
