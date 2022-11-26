import json

import stripe
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas, security
from app.database import get_database
from app.environ import ENVIRONMENT, STRIPE_SIGNING_KEY

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

    print(json.dumps(event))

    if event['type'] == 'checkout.session.completed':
        checkout_session = event['data']['object']
        order_id = int(checkout_session['metadata']['order_id'])

        stmt = select(models.Order).where(models.Order.id == order_id)
        order = (await db.execute(stmt)).scalars().first()

        order.stripe_id = checkout_session['payment_intent']
        order.status = models.OrderStatus.ORDERED

    