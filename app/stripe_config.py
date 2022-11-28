import stripe


class StripeShippingRateError(Exception):
    """Raised when a shipping option is not found."""
    pass

shipping_rates = {
    'express': None,
    'standard': None,
    'complimentary': None,
}

def load_shipping_rates():
    res = stripe.ShippingRate.list(active=True)

    for rate in res.auto_paging_iter():
        rate_type = rate['metadata'].get('type')
        if rate_type is not None and rate_type in shipping_rates:
            shipping_rates[rate_type] = rate['id']

    if None in shipping_rates.values():
        raise StripeShippingRateError("\nNot all shipping options are available.\nMake sure to run `python manage stripe setup` to setup the shipping options.")