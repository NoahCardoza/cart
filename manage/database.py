import asyncio

import bcrypt
from app.database import async_session_factory
from app.models import Category, Product, User, create_all_tables
from typer import Option, Typer

from manage.utils import coro

db_app = Typer(
    help="A collection of commands to help with database management.")


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
        await populate_database()


async def populate_database():
    async with async_session_factory() as session:
        # create default users
        users = {
            role: User(**details)
            for role, details in [
                (
                    'admin', {
                        'firstname': "Jeff",
                        'lastname': "Bezos",
                        'email': "jeff.bezos@sjsu.edu",
                        'password': bcrypt.hashpw(b"superuser", bcrypt.gensalt()).decode(),
                        'is_superuser': True,
                    }
                ),
                (
                    'employee', {
                        'firstname': "Amy",
                        'lastname': "Dyken",
                        'email': "amy.dyken@sjsu.edu",
                        'password': bcrypt.hashpw(b"employee", bcrypt.gensalt()).decode(),
                        'is_employee': True,
                    }
                ),
                (
                    'customer', {
                        'firstname': "Morgan",
                        'lastname': "Freemen",
                        'email': "morgan.freemen@sjsu.edu",
                        'password': bcrypt.hashpw(b"customer", bcrypt.gensalt()).decode(),
                    }
                )
            ]
        }
        session.add_all(users.values())

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

        # create default products
        products = {
            details['name']: Product(**details) for details in [
                {
                    "name": "Apples",
                    "description": "Fresh apples from local farms",
                    "image_url": "https://images.unsplash.com/photo-1569870499705-504209102861?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=830&q=80",
                    "category_id": categories["Fruits"].id,
                    "quantity": 20,
                    "price": 1.99,
                },
                {
                    "name": "Oranges",
                    "description": "Fresh oranges from local farms",
                    "image_url": "https://images.unsplash.com/photo-1611080626919-7cf5a9dbab5b?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=870&q=80",
                    "category_id": categories["Fruits"].id,
                    "quantity": 20,
                    "price": 1.99,
                },
                {
                    "name": "Peaches",
                    "description": "Fresh peaches from local farms",
                    "image_url": "https://images.unsplash.com/photo-1629226182720-f0a169fc9a8e?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=870&q=80",
                    "category_id": categories["Fruits"].id,
                    "quantity": 20,
                    "price": 1.99,
                },
                {
                    "name": "Strawberries",
                    "description": "Fresh strawberries from local farms",
                    "image_url": "https://images.unsplash.com/photo-1543158181-e6f9f6712055?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80",
                    "category_id": categories["Fruits"].id,
                    "quantity": 20,
                    "price": 1.99,
                },
                {
                    "name": "Apricots",
                    "description": "Fresh apricots from local farms",
                    "image_url": "https://images.unsplash.com/photo-1592681814168-6df0fa93161b?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80",
                    "category_id": categories["Fruits"].id,
                    "quantity": 20,
                    "price": 1.99,
                },
                {
                    "name": "Bananas",
                    "description": "Fresh bananas from local farms",
                    "image_url": "https://images.unsplash.com/photo-1603833665858-e61d17a86224?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=654&q=80",
                    "category_id": categories["Fruits"].id,
                    "quantity": 20,
                    "price": 1.99,
                },
                {
                    "name": "Black Berries",
                    "description": "Fresh black berries from local farms",
                    "image_url": "https://images.unsplash.com/photo-1562845029-d1b530d4cfd3?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80",
                    "category_id": categories["Fruits"].id,
                    "quantity": 20,
                    "price": 1.99,
                },
                {
                    "name": "Raspberries",
                    "description": "Fresh raspberries from local farms",
                    "image_url": "https://images.unsplash.com/photo-1577069861033-55d04cec4ef5?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=928&q=80",
                    "category_id": categories["Fruits"].id,
                    "quantity": 20,
                    "price": 1.99,
                },
            ]}
        session.add_all(products.values())

        await session.commit()


@db_app.command()
@coro
async def populate():
    """Populate the database with default data"""
    await populate_database()
