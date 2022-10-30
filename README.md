# Product Goose (Backend)

A group project for CMPE 131 at SJSU.

## Setup

To run the project, you need to have `python 3.9` and `pipenv` installed.

If you don't have `pipenv`, you can install it by running `python -m pip install pipenv`.

Then, run `python -m pipenv install` to install all the dependencies.

When you are done, run `python -m pipenv run uvicorn app:app --reload` to run the project.

### ENV

Uvicorn will look for a `.env` file in the root directory. Copy the `.env.example` file and rename it to `.env`. 
Then, fill in any values that need configuration.

### Database

To run the project, you need to have a database running.

To run the database, you need to have `docker` and `docker-compose` installed.

You can start the database by running `docker-compose up -d`. When you are done, you can stop the 
database by running `docker-compose down`.

After the database is running, you need to create all the required tables. To do so, run 
`python manage db build`.

## API Documentation

The API documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and 
[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc). They both show the same information but 
in slightly different ways formats.

## Comunicating with the frontend

For simplicity and becasue we are using SSR, we are using JWT encoded cookies to track user sessions.
The only caveat is that when run locally, the frontend and backend need to be running on the same domain.
A simple solution is to spin up a reverse proxy like nginx and have it proxy requests to both the
the frontend dev server and the backend dev server.

To do this, just run `docker-compose up nginx` in the root directory. This will spin up a nginx server.
If you want to run the local frontend on the staging server, you will need to edit line `12` in
`/nginx/nginx.conf`, changing `http://host.docker.internal:8000/` to `https://produce-goose-backend-stg.herokuapp.com/`.

**If you make these changes, remember not to commit them.**

## Frameworks and Libraries

+ [FastAPI](https://fastapi.tiangolo.com)
+ [Pydantic](https://pydantic-docs.helpmanual.io)
+ [SQLAlchemy](https://docs.sqlalchemy.org/en/14/intro.html)
