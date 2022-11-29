import json
from datetime import datetime
from traceback import print_exc

import requests
import stripe
from app import models
from app.database import get_database
from app.environ import ENVIRONMENT, POSITIONSTACK_API_KEY, STRIPE_SIGNING_KEY
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

webhook_router = APIRouter()


@webhook_router.post("/stripe/")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_database)
):

    request_body = await request.body()

    # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
    try:
        event = stripe.Webhook.construct_event(
            request_body,
            request.headers["stripe-signature"],
            STRIPE_SIGNING_KEY
        )
    except (stripe.error.SignatureVerificationError, KeyError) as e:
        if ENVIRONMENT == "production":  # pragma: no cover
            raise HTTPException(status_code=400, detail=f"Bad signature.")
        else:  # pragma: no cover
            event = json.loads(request_body)

    if event['type'] == 'checkout.session.completed':
        checkout_session = event['data']['object']
        order_id = int(checkout_session['metadata']['order_id'])

        stmt = select(models.Order).where(models.Order.id == order_id)
        order = (await db.execute(stmt)).scalars().first()

        order.stripe_id = checkout_session['payment_intent']
        order.status = models.OrderStatus.ORDERED

        order.amount_total = round(checkout_session['amount_total'] / 100, 2)
        order.amount_subtotal = round(
            checkout_session['amount_subtotal'] / 100, 2)
        order.amount_tax = round(
            checkout_session['total_details']['amount_tax'] / 100, 2)
        order.amount_shipping = round(
            checkout_session['total_details']['amount_shipping'] / 100, 2)

        address = checkout_session['shipping_details']['address']
        short_address = address['line1'] + (" " + address['line2']
                                            if address['line2'] else '') + ', ' + address['city']
        long_address = short_address + ', ' + \
            address['state'] + ', ' + address['postal_code'] + \
            ', ' + address['country']

        try:
            res = requests.get('http://api.positionstack.com/v1/forward', params={
                'access_key': POSITIONSTACK_API_KEY,
                'query': long_address,
                'limit': 1,
            })

            # TODO: find better API throws too many 502 errors
            if res.status_code == 200:
                data = res.json()

                if len(data['data']) > 0:
                    order.latitude = data['data'][0]['latitude']
                    order.longitude = data['data'][0]['longitude']
        except json.JSONDecodeError:
            # known issue returning html when overloaded
            pass
        except TypeError:
            # known issue with positionstack API returning: {'data': [[]]}
            pass
        except Exception as e:
            # ignore all other errors but report them
            print_exc(e)

        order.address = short_address
        order.updated_at = datetime.utcnow()
