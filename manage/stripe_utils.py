import stripe
from typer import Typer

from app.stripe_config import StripeShippingRateError, load_shipping_rates

stripe_app = Typer(
    help="A collection of commands to help with Stripe.")

delivery_options = [
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
def setup():
    """Create all necessary Stripe objects."""

    try:
        load_shipping_rates()
        print('Shipping options already loaded.')
    except StripeShippingRateError:
        for option in delivery_options:
            stripe.ShippingRate.create(**option)
        print('Shipping options loaded.')
