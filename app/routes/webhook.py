import json

import requests
import stripe
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.database import get_database
from app.environ import ENVIRONMENT, POSITIONSTACK_API_KEY, STRIPE_SIGNING_KEY

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
        if ENVIRONMENT == "production":
            raise HTTPException(status_code=400, detail=f"Bad signature.")
        else:
            event = json.loads(request_body)

    if event['type'] == 'checkout.session.completed':
        checkout_session = event['data']['object']
        order_id = int(checkout_session['metadata']['order_id'])

        stmt = select(models.Order).where(models.Order.id == order_id)
        order = (await db.execute(stmt)).scalars().first()

        order.stripe_id = checkout_session['payment_intent']
        order.status = models.OrderStatus.ORDERED

        order.amount_total = round(checkout_session['amount_total'] / 100, 2)
        order.amount_subtotal = round(checkout_session['amount_subtotal'] / 100, 2)
        order.amount_tax = round(checkout_session['total_details']['amount_tax'] / 100, 2)
        order.amount_shipping = round(checkout_session['total_details']['amount_shipping'] / 100, 2)
        
        address = checkout_session['shipping_details']['address']
        short_address = address['line1'] + (" " + address['line2'] if address['line2'] else '') + ', ' + address['city']
        long_address = short_address + ', ' + address['state'] + ', ' + address['postal_code'] + ', ' + address['country']

        res = requests.get('http://api.positionstack.com/v1/forward', params={
                'access_key': POSITIONSTACK_API_KEY,
                'query': long_address,
                'limit': 1,
        }).json()

        if len(res['data']) > 0:
            order.latitude = res['data'][0]['latitude']
            order.longitude = res['data'][0]['longitude']

        order.address = short_address
