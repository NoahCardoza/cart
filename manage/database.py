import stripe
from typer import Option, Typer

from app.database import async_session_factory
from app.models import (Category, Order, OrderItem, OrderStatus, Product, User,
                        create_all_tables)
from app.security import pwd_context
from manage.utils import coro

db_app = Typer(
    help="A collection of commands to help with database management. Use $DATABASE_URL to specify a the database URL."
)


@db_app.command()
@coro
async def build(
    populate: bool = Option(
        False, "--populate", "-p", help="Populate the database with sample data. Alias to `db populate`."),
    drop_all: bool = Option(
        False, "--drop", "-d", help="Drop all tables before building.")
):
    """Build the database tables."""
    await create_all_tables(drop_all=drop_all)
    if populate:
        await populate_database(async_session_factory)


def upsert_stripe_contact(email: str, name: str):
    """Upsert a contact in Stripe.

    Args:
        email (str): The email of the contact.
        name (str): The name of the contact.
    """
    try:
        customers = stripe.Customer.search(
            query=f"email:'{email}'"
        )['data']

        if len(customers) == 0:
            return stripe.Customer.create(
                name=name,
                email=email
            )
        return customers[0]
    except stripe.error.InvalidRequestError:
        pass

async def populate_database(session_factory):
    async with session_factory() as session:
        # create default users
        users = {
            role: User(**details, stripe_id=upsert_stripe_contact(details['email'], f"{details['firstname']} {details['lastname']}")['id'])
            for role, details in [
                (
                    'admin', {
                        'firstname': "Jeff",
                        'lastname': "Bezos",
                        'email': "jeff.bezos@sjsu.edu",
                        'password': pwd_context.hash("superuser"),
                        'is_superuser': True,
                    }
                ),
                (
                    'employee', {
                        'firstname': "Amy",
                        'lastname': "Dyken",
                        'email': "amy.dyken@sjsu.edu",
                        'password': pwd_context.hash("employee"),
                        'is_employee': True,
                    }
                ),
                (
                    'customer', {
                        'firstname': "Morgan",
                        'lastname': "Freemen",
                        'email': "morgan.freemen@sjsu.edu",
                        'password': pwd_context.hash("customer"),
                    }
                )
            ]
        }

        session.add_all(users.values())

        await session.commit()
        # await session.refresh_all(users.values())

        # create default categories
        categories = {
            details["name"]: Category(**details) for details in [
                {
                    "name": "Vegetables",
                    "description": "Fresh vegetables from local farms",
                    "image_url": "https://images.unsplash.com/photo-1597362925123-77861d3fbac7?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80",
                },
                {
                    "name": "Fruits",
                    "description": "Fresh fruits from local farms",
                    "image_url": "https://images.unsplash.com/photo-1610832958506-aa56368176cf?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80",
                },
                {
                    "name": "Meats",
                    "description": "Fresh meats from local farms",
                    "image_url": "https://images.unsplash.com/photo-1632154023554-c2975e9be348?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=774&q=80",
                },
                {
                    "name": "Grains",
                    "description": "Fresh grains from local farms",
                    "image_url": "https://images.unsplash.com/photo-1623066798929-946425dbe1b0?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80",
                },
                {
                    "name": "Eggs & Dairy",
                    "description": "Fresh eggs & dairy from local farms",
                    "image_url": "https://images.unsplash.com/photo-1617049092088-8771a80edde2?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1480&q=80",
                },
                {
                    "name": "Nuts & Seeds",
                    "description": "Fresh nuts & seeds from local farms",
                    "image_url": "https://images.unsplash.com/photo-1543208541-0961a29a8c3d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80"
                },
                {
                    "name": "Spices & Herbs",
                    "description": "Fresh spices and herbs from local farms",
                    "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80",
                },
                {
                    "name": "Supplements",
                    "description": "Fresh supplements from local farms",
                    "image_url": "https://images.unsplash.com/photo-1627467959547-8e44da7aa00a?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1374&q=80"
                },
            ]
        }
        session.add_all(categories.values())

        # commit changes to the database so we can use the ids
        await session.commit()
        # await session.refresh_all(categories.values())

        # create default products
        products = {
            details['name']: Product(**details) for details in [
                 {
                    "name": "Apples",
                    "description": "Fresh apples from local farms",
                    "image_url": "https://images.unsplash.com/photo-1569870499705-504209102861?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=830&q=80",
                    "category_id": categories["Fruits"].id,
                    "quantity": 20,
                    "weight": 0.5,
                    "price": 2.53,
                },
                {
                    "name": "Oranges",
                    "description": "Fresh oranges from local farms",
                    "image_url": "https://images.unsplash.com/photo-1611080626919-7cf5a9dbab5b?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=870&q=80",
                    "category_id": categories["Fruits"].id,
                    "quantity": 20,
                    "weight": 0.7,
                    "price": 1.25,
                },
                {
                    "name": "Peaches",
                    "description": "Fresh peaches from local farms",
                    "image_url": "https://images.unsplash.com/photo-1629226182720-f0a169fc9a8e?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=870&q=80",
                    "category_id": categories["Fruits"].id,
                    "quantity": 20,
                    "weight": 0.8,
                    "price": 2.99,
                },
                {
                    "name": "Strawberries",
                    "description": "Fresh strawberries from local farms",
                    "image_url": "https://images.unsplash.com/photo-1543158181-e6f9f6712055?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80",
                    "category_id": categories["Fruits"].id,
                    "quantity": 20,
                    "weight": 0.2,
                    "price": 4.49,
                },
                {
                    "name": "Apricots",
                    "description": "Fresh apricots from local farms",
                    "image_url": "https://images.unsplash.com/photo-1592681814168-6df0fa93161b?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80",
                    "category_id": categories["Fruits"].id,
                    "quantity": 20,
                    "weight": 0.3,
                    "price": 2.36,  
                },
                {
                    "name": "Bananas",
                    "description": "Fresh bananas from local farms",
                    "image_url": "https://images.unsplash.com/photo-1603833665858-e61d17a86224?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=654&q=80",
                    "category_id": categories["Fruits"].id,
                    "quantity": 20,
                    "weight": 0.4,
                    "price": 1.69,
                },
                {
                    "name": "Black Berries",
                    "description": "Fresh black berries from local farms",
                    "image_url": "https://images.unsplash.com/photo-1562845029-d1b530d4cfd3?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80",
                    "category_id": categories["Fruits"].id,
                    "quantity": 20,
                    "weight": 0.6,
                    "price": 1.99,
                },
                {
                    "name": "Raspberries",
                    "description": "Fresh raspberries from local farms",
                    "image_url": "https://images.unsplash.com/photo-1577069861033-55d04cec4ef5?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=928&q=80",
                    "category_id": categories["Fruits"].id,
                    "quantity": 20,
                    "weight": 0.6,
                    "price": 2.79,
                },
                 {
                    "name": "Broccoli",
                    "description": "Fresh broccoli from local farms",
                    "image_url": "https://images.unsplash.com/photo-1584270354949-c26b0d5b4a0c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2OTE4NDE3Ng&ixlib=rb-4.0.3&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Vegetables"].id,
                    "quantity": 20,
                    "weight": 0.2,
                    "price": 2.99,
                },
                {
                    "name": "Cabbage",
                    "description": "Fresh cabbage from local farms",
                    "image_url": "https://images.unsplash.com/photo-1594282486552-05b4d80fbb9f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY1NDE0ODk0MQ&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Vegetables"].id,
                    "quantity": 20,
                    "weight": 0.2,
                    "price": 1.79,
                },
                {
                    "name": "Lettuce",
                    "description": "Fresh lettuce from local farms",
                    "image_url": "https://images.unsplash.com/photo-1591193144634-a2bf060fdb36?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2OTI0MTMxOA&ixlib=rb-4.0.3&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Vegetables"].id,
                    "quantity": 20,
                    "weight": 0.2,
                    "price": 1.99,
                },
                 {
                    "name": "Carrots",
                    "description": "Fresh carrots from local farms",
                    "image_url": "https://images.unsplash.com/photo-1639427444459-85a1b6ac2d68?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2OTI0MTM1Mg&ixlib=rb-4.0.3&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Vegetables"].id,
                    "quantity": 20,
                    "weight": 0.2,
                    "price": 1.99,
                },
                 {
                    "name": "Tomatoes",
                    "description": "Fresh tomatoes from local farms",
                    "image_url": "https://images.unsplash.com/photo-1582284540020-8acbe03f4924?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTYyNjM1NTc4Mw&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Vegetables"].id,
                    "quantity": 20,
                    "weight": 0.2,
                    "price": 1.99,
                },
                 {
                    "name": "Onions",
                    "description": "Fresh onions from local farms",
                    "image_url": "https://images.unsplash.com/photo-1620574387735-3624d75b2dbc?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY1OTIxMzE5NA&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Vegetables"].id,
                    "quantity": 20,
                    "weight": 0.2,
                    "price": 1.69,
                },
                {
                    "name": "Potatoes",
                    "description": "Fresh potatoes from local farms",
                    "image_url": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY1MDk5MTU0Mg&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Vegetables"].id,
                    "quantity": 20,
                    "weight": 0.2,
                    "price": 0.99,
                },
                 {
                    "name": "Spinach",
                    "description": "Fresh spinach from local farms",
                    "image_url": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2OTI0MTQ0NA&ixlib=rb-4.0.3&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Vegetables"].id,
                    "quantity": 20,
                    "weight": 0.2,
                    "price": 1.99,
                },
                 {
                    "name": "Ribeye Steaks",
                    "description": "Fresh ribeye steaks from local farms",
                    "image_url": "https://images.unsplash.com/photo-1623241899289-e9a64b02150d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2NzQxNDc2Mg&ixlib=rb-4.0.3&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Meats"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 11.99,
                },
                    {
                    "name": "Porkchops",
                    "description": "Fresh porkchops from local farms",
                    "image_url": "https://images.unsplash.com/photo-1628268909376-e8c44bb3153f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY1ODA1OTQ4Nw&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Meats"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 4.29,
                },
                  {
                    "name": "Lambchops",
                    "description": "Fresh lambchops from local farms",
                    "image_url": "https://images.unsplash.com/photo-1619711667542-c049700dd9e0?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2OTI0MTY0MA&ixlib=rb-4.0.3&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Meats"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 8.99,
                },
                  {
                    "name": "Ground Beef",
                    "description": "Fresh ground beef from local farms",
                    "image_url": "https://images.unsplash.com/photo-1613985208269-e8f4dbcc7576?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2NDczOTkzNg&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Meats"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 5.97,
                },
                {
                    "name": "Turkey",
                    "description": "Fresh turkey from local farms",
                    "image_url": "https://images.unsplash.com/photo-1574672281194-db420378032d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2OTI0MTcxMg&ixlib=rb-4.0.3&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Meats"].id,
                    "quantity": 20,
                    "weight": 12.0,
                    "price": 23.99,
                },
                  {
                    "name": "Chicken Thighs",
                    "description": "Fresh chicken thighs from local farms",
                    "image_url": "https://images.unsplash.com/photo-1638439430466-b2bb7fdc1d67?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2Mzk5NjA5NA&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Meats"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 9.99,
                },
                {
                    "name": "Chicken Breast",
                    "description": "Fresh chicken breast from local farms",
                    "image_url": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY1NzQ4NDk0NQ&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Meats"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 10.99,
                },
                  {
                    "name": "Veal",
                    "description": "Fresh veal from local farms",
                    "image_url": "https://images.unsplash.com/photo-1615937657715-bc7b4b7962c1?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY1OTQ2Mjk0MQ&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Meats"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 29.99,
                },
                  {
                    "name": "Wheat Bread",
                    "description": "Fresh wheat bread from local farms",
                    "image_url": "https://images.unsplash.com/photo-1535912562650-f95ddac3f4a7?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2OTI0Nzk4OQ&ixlib=rb-4.0.3&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Grains"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 4.99,
                },
                 {
                    "name": "White Bread",
                    "description": "Fresh white bread from local farms",
                    "image_url": "https://images.unsplash.com/photo-1621930599436-32ba90132e3e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2OTI0ODA0OQ&ixlib=rb-4.0.3&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Grains"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 3.99,
                },
                  {
                    "name": "Jasmine Rice",
                    "description": "Fresh jasmine rice from local farms",
                    "image_url": "https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxhbGx8fHx8fHx8fHwxNjIwNjYzMDQ2&ixlib=rb-1.2.1&q=80&w=1080&utm_source=unsplash_source&utm_medium=referral&utm_campaign=api-credit",
                    "category_id": categories["Grains"].id,
                    "quantity": 20,
                    "weight": 50.0,
                    "price": 24.99,
                },
                {
                    "name": "Barley",
                    "description": "Fresh barley from local farms",
                    "image_url": "https://cdn-prod.medicalnewstoday.com/content/images/articles/295/295268/barley-grains-in-a-wooden-bowl.jpg",
                    "category_id": categories["Grains"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 4.99,
                },
                {
                    "name": "Oats",
                    "description": "Fresh oats from local farms",
                    "image_url": "https://images.unsplash.com/photo-1614961233913-a5113a4a34ed?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2OTI0ODE3MQ&ixlib=rb-4.0.3&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Grains"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 1.99,
                },
                {
                    "name": "Wheat",
                    "description": "Fresh wheat from local farms",
                    "image_url": "https://images.unsplash.com/photo-1614414051203-03a7dc75eca5?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2OTI0ODI0Mw&ixlib=rb-4.0.3&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Grains"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 2.99,
                },
                {
                    "name": "Brown Rice",
                    "description": "Fresh brown rice from local farms",
                    "image_url": "https://images.unsplash.com/photo-1613728913341-8f29b02b8253?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY0MDk0MDcxNg&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Grains"].id,
                    "quantity": 20,
                    "weight": 5.0,
                    "price": 8.99,
                },
                {
                    "name": "Macaroni",
                    "description": "Fresh macaroni from local farms",
                    "image_url": "https://images.unsplash.com/photo-1607546965882-e025ff0edc61?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2OTI0ODI5Mg&ixlib=rb-4.0.3&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Grains"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 4.99,
                },
                {
                    "name": "Eggs",
                    "description": "Fresh eggs from local farms",
                    "image_url": "https://images.unsplash.com/photo-1593584785033-9c7604d0863f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2NDI2OTc2OA&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Eggs & Dairy"].id,
                    "quantity": 20,
                    "weight": 1.5,
                    "price": 3.99,
                },
                 
                
                 {
                    "name": "Milk",
                    "description": "Fresh milk from local farms",
                    "image_url": "https://images.unsplash.com/photo-1550583724-b2692b85b150?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2MzgwODc3NQ&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Eggs & Dairy"].id,
                    "quantity": 20,
                    "weight": 6.0,
                    "price": 6.99,
                },  
                 {
                    "name": "Cheese",
                    "description": "Fresh cheese from local farms",
                    "image_url": "https://images.unsplash.com/photo-1589881133595-a3c085cb731d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2OTI0ODU3Mw&ixlib=rb-4.0.3&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Eggs & Dairy"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 2.99,
                },
                 {
                    "name": "Yogurt",
                    "description": "Fresh yogurts from local farms",
                    "image_url": "https://images.unsplash.com/photo-1593999419634-455e51714dca?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2OTI0ODYyNQ&ixlib=rb-4.0.3&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Eggs & Dairy"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 3.99,
                },
                {
                    "name": "Butter",
                    "description": "Fresh butter from local farms",
                    "image_url": "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY0NTY3NDM5Ng&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Eggs & Dairy"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 4.99,
                },
                 {
                    "name": "Ice Cream",
                    "description": "Fresh ice cream from local farms",
                    "image_url": "https://images.unsplash.com/photo-1633933358116-a27b902fad35?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY1Nzk4NDk4OQ&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Eggs & Dairy"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 8.99,
                },
                 {
                    "name": "Whipped Cream",
                    "description": "Fresh whipped cream from local farms",
                    "image_url": "https://images.unsplash.com/photo-1589396575653-c09c794ff6a6?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2MzkyODUwNw&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Eggs & Dairy"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 3.99,
                },
                 {
                    "name": "Condensed Milk",
                    "description": "Fresh condensed milk from local farms",
                    "image_url": "https://www.thespruceeats.com/thmb/uG3R7kOOuAo2BQJ0jcy-a-ISyWY=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/homemade-condensed-milk-1500-58ae094c5f9b58a3c91e41ba-5b3d38a546e0fb0037bd2d94.jpg",
                    "category_id": categories["Eggs & Dairy"].id,
                    "quantity": 20,
                    "weight": 1.02,
                    "price": 6.99,
                },
                 {
                    "name": "Almonds",
                    "description": "Fresh almonds from local farms",
                    "image_url": "https://www.rachelcooks.com/wp-content/uploads/2022/02/olive-oil-roasted-almonds-1500-11-square.jpg",
                    "category_id": categories["Nuts & Seeds"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 1.99,
                },
                 {
                    "name": "Macadamia Nuts",
                    "description": "Fresh macadamia nuts from local farms",
                    "image_url": "https://images.unsplash.com/photo-1579293675541-10fcb3725a19?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2OTI0OTExNQ&ixlib=rb-4.0.3&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Nuts & Seeds"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 1.99,
                },
                  {
                    "name": "Cashews",
                    "description": "Fresh cashews from local farms",
                    "image_url": "https://images.unsplash.com/photo-1509912760195-4f6cfd8cce2c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2MTAxOTUxNA&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Nuts & Seeds"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 1.99,
                },
                 {
                    "name": "Walnuts",
                    "description": "Fresh walnuts from local farms",
                    "image_url": "https://images.unsplash.com/photo-1597919926163-9419065218b4?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2OTI0OTE2Mw&ixlib=rb-4.0.3&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Nuts & Seeds"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 1.99,
                },
                 {
                    "name": "Peanuts",
                    "description": "Fresh peanuts from local farms",
                    "image_url": "https://images.unsplash.com/photo-1575399872095-9363bf262e64?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY1ODUyNzQ5Ng&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Nuts & Seeds"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 1.99,
                },
                 {
                    "name": "Sunflower Seeds",
                    "description": "Fresh sunflower seeds from local farms",
                    "image_url": "https://images.unsplash.com/photo-1555191499-4e58f5d7eb85?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY0NzQ5Nzc2NA&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Nuts & Seeds"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 1.99,
                },
                 {
                    "name": "Honey Glazed Almonds",
                    "description": "Fresh honey glazed almonds from local farms",
                    "image_url": "https://paleogrubs.com/wp-content/uploads/2018/10/5a-honey-mustard-roasted-almonds-square-1200x900-cropped.jpg",
                    "category_id": categories["Nuts & Seeds"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 3.99,
                },
                 {
                    "name": "Pumpkin Seeds",
                    "description": "Fresh pumpkin seeds from local farms",
                    "image_url": "https://images.unsplash.com/photo-1508061217390-994bc42bccf7?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY1MzA0MzMwNA&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Nuts & Seeds"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 1.99,
                },
                      {
                    "name": "Cayenne",
                    "description": "Fresh cayenne from local farms",
                    "image_url": "http://specialtyproduce.com/sppics/6127-a.png",
                    "category_id": categories["Spices & Herbs"].id,
                    "quantity": 20,
                    "weight": 0.5,
                    "price": 4.99,
                },
                 {
                    "name": "Paprika",
                    "description": "Fresh paprika from local farms",
                    "image_url": "https://www.tastingtable.com/img/gallery/everything-you-need-to-know-about-paprika/intro-1648914630.jpg",
                    "category_id": categories["Spices & Herbs"].id,
                    "quantity": 20,
                    "weight": 0.4,
                    "price": 4.99,
                },
                 {
                    "name": "Garlic Salt",
                    "description": "Fresh garlic salt from local farms",
                    "image_url": "https://therustyspoon.com/wp-content/uploads/2021/12/Can-Garlic-Salt-Be-Used-In-PlaceOf-Garlic-Powder.jpg",
                    "category_id": categories["Spices & Herbs"].id,
                    "quantity": 20,
                    "weight": 0.4,
                    "price": 3.99,
                },
                 {
                    "name": "Onion Powder",
                    "description": "Fresh onion powder from local farms",
                    "image_url": "https://cdnimg.webstaurantstore.com/images/products/large/80212/1824797.jpg",
                    "category_id": categories["Spices & Herbs"].id,
                    "quantity": 20,
                    "weight": 0.4,
                    "price": 4.99,
                },
                 {
                    "name": "Thyme",
                    "description": "Fresh thyme from local farms",
                    "image_url": "https://images.unsplash.com/photo-1590673560914-36412602071d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2NTY1NjY5MQ&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Spices & Herbs"].id,
                    "quantity": 20,
                    "weight": 0.2,
                    "price": 5.99,
                },
                 {
                    "name": "Sage",
                    "description": "Fresh sage from local farms",
                    "image_url": "https://images.unsplash.com/photo-1617314608196-356afaecfe7c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2MjA5MTYyMA&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Spices & Herbs"].id,
                    "quantity": 20,
                    "weight": 0.3,
                    "price": 3.99,
                },
                 {
                    "name": "Rosemary",
                    "description": "Fresh rosemary from local farms",
                    "image_url": "https://images.unsplash.com/photo-1607721098274-e54cbfab475d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2MjAzMjY5OQ&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Spices & Herbs"].id,
                    "quantity": 20,
                    "weight": 0.3,
                    "price": 4.99,
                },
                 {
                    "name": "Basil",
                    "description": "Fresh basil from local farms",
                    "image_url": "https://images.unsplash.com/photo-1500420254515-0faefa2dac99?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY2OTI0OTc0NQ&ixlib=rb-4.0.3&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080",
                    "category_id": categories["Spices & Herbs"].id,
                    "quantity": 20,
                    "weight": 0.2,
                    "price": 5.99,
                },
                 {
                    "name": "Whey Protein",
                    "description": "Fresh whey protein from local farms",
                    "image_url": "https://images.heb.com/is/image/HEBGrocery/002838513?fit=constrain,1&wid=800&hei=800&fmt=jpg&qlt=85,0&resMode=sharp2&op_usm=1.75,0.3,2,0",
                    "category_id": categories["Supplements"].id,
                    "quantity": 20,
                    "weight": 2.3,
                    "price": 49.99,
                },
                 {
                    "name": "Isolate Protein",
                    "description": "Fresh isolate protein from local farms",
                    "image_url": "https://i5.walmartimages.com/asr/58803595-9201-4dbd-8d72-4a6fd0ac1d4a.f7abb7fb25e757466ab71b8dd0ac0eb3.jpeg",
                    "category_id": categories["Supplements"].id,
                    "quantity": 20,
                    "weight": 2.0,
                    "price": 49.99,
                },
                 {
                    "name": "Creatine",
                    "description": "Fresh creatine from local farms",
                    "image_url": "https://www.nutrabio.com/images/product/600x927/23014.jpg",
                    "category_id": categories["Supplements"].id,
                    "quantity": 20,
                    "weight": 2.2,
                    "price": 54.99,
                },
                 {
                    "name": "Melatonin Gummies",
                    "description": "Fresh melatonin gummies from local farms",
                    "image_url": "https://www.wellnessverge.com/uploads/articles/olly-sleep-gummies-1641946237.jpg",
                    "category_id": categories["Supplements"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 10.99,
                },
                 {
                    "name": "Antioxidant Green Powder",
                    "description": "Fresh antioxidant green powder from local farms",
                    "image_url": "https://www.eatthis.com/wp-content/uploads/sites/4/2020/12/green-powder.jpg?quality=82&strip=1",
                    "category_id": categories["Supplements"].id,
                    "quantity": 20,
                    "weight": 1.4,
                    "price": 20.99,
                },
                 {
                    "name": "Vitamin C Gummies",
                    "description": "Fresh vitamin C gummies from local farms",
                    "image_url": "https://www.dearcrissy.com/wp-content/uploads/2015/08/Citrus-vitamin-c-burst-gummies-5-650x978.jpg",
                    "category_id": categories["Supplements"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 7.99,
                },
                 {
                    "name": "Vitamin A Gummies",
                    "description": "Fresh vitamin A gummies from local farms",
                    "image_url": "https://i0.wp.com/images-prod.healthline.com/hlcmsresource/images/AN_images/gummy-gummies-vitamins-1296x728-header.jpg?w=1155&h=1528",
                    "category_id": categories["Supplements"].id,
                    "quantity": 20,
                    "weight": 1.0,
                    "price": 7.99,
                },
                {
                    "name": "Hair Loss Pills",
                    "description": "Fresh hair loss pills from local farms",
                    "image_url": "https://i0.wp.com/post.medicalnewstoday.com/wp-content/uploads/sites/3/2022/06/Olumiant_alopecia_shutterstock_2159010883_Header-1024x575.jpg?w=1155&h=1528",
                    "category_id": categories["Supplements"].id,
                    "quantity": 20,
                    "weight": 1.3,
                    "price": 15.99,
                },
            ]}
        session.add_all(products.values())
        
        await session.commit()
        # await session.refresh_all(products.values())

        past_orders = [
            Order(
                user_id=users["customer"].id,
                status=OrderStatus.CART,
                items=[
                    OrderItem(
                        product_id=products["Apples"].id,
                        quantity=1,
                    )
                ],
                amount_total = round(5.99 + (products["Apples"].price * 1.098), 2),
                amount_subtotal = products["Apples"].price,
                amount_shipping = 5.99,
                amount_tax = round(products["Apples"].price * 0.098, 2),
                address="123 Main St, San Jose",
            ),
            Order(
                user_id=users["employee"].id,
                status=OrderStatus.CART,
                items=[
                    OrderItem(
                        product_id=products["Apples"].id,
                        quantity=1,
                    )
                ],
                amount_total = round(5.99 + (products["Apples"].price * 1.098), 2),
                amount_subtotal = products["Apples"].price,
                amount_shipping = 5.99,
                amount_tax = round(products["Apples"].price * 0.098, 2),
                address="321 Main St, San Jose",
            )
        ]

        session.add_all(past_orders)
        await session.commit()
        
        


@db_app.command()
@coro
async def populate():
    """Populate the database with default data"""
    await populate_database(async_session_factory)
