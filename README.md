# Product Goose (Backend)

A group project for CMPE 131 at SJSU.

## Setup

To run the project, you need to have `python 3.10` and `pipenv` installed.

If you don't have `pipenv`, you can install it by running `pip install pipenv`.

Then, run `python -m pipenv install` to install all the dependencies.

When you are done, run `python -m pipenv run uvicorn app:app --reload` to run the project.

### Impotant Notes

Most of these commands assume you are at the root of the project. They also assume you are
using inside the virtual environment created by `pipenv`. To activate the virtual environment,
run `pipenv shell`.

### Common Issues

#### Error: pip not found

If you get an error saying `pip not found`, you can try running `python -m pip <rest-of-the-command>`.

#### Error: pipenv not found

If you get an error saying `pipenv not found`, you can try running `python -m pipenv <rest-of-the-command>` instead.

#### Error: python not found (Windows)

If you get an error saying `python not found`, you can replace `python` with `py` and try running `py <rest-of-the-command>` instead.

If you are still having issues, your `PATH` environment variable might not be set correctly. [See](https://www.youtube.com/watch?v=hZLJKddSAUE)

#### Multiple python versions (Windows)

If you have multiple python versions installed, you can try running `py -3.10 <rest-of-the-command>` instead.

#### Multiple python versions (Mac)

If you have multiple python versions installed, you can try running `python3.10 <rest-of-the-command>` instead.

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

### Stripe

1. Make sure you have a Stripe account. If you don't, you can create one [here](https://dashboard.stripe.com/register).
2. Go to the [Stripe dashboard](https://dashboard.stripe.com/test/dashboard) and click on `Developers` -> `API keys`.
3. Copy the `Publishable key` and `Secret key` and paste them in the `.env` file.
4. If you are running locally install [Stripe CLI](https://stripe.com/docs/stripe-cli) and run `stripe listen --forward-to localhost:8080/api/webhook/stripe/`.
    1. Otherwise: Go to the [Stripe dashboard](https://dashboard.stripe.com/test/dashboard) and click on `Developers` -> `Webhooks`.
    2. Click on `Add endpoint`.
    3. Paste the URL of your backend in the `Endpoint URL` field. For example, if your backend is running on `https://www.publichost.com` then the URL would be `https://www.publichost.com/api/webhook/stripe/`.
7. Setup the tax rates for your business. You can do so by going to the [Stripe Tax Rates Dashboard](https://dashboard.stripe.com/test/tax-rates).
8. Setup the shipping rates by running `python manage stripe setup`.
  
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

## Testing

To run the tests, run `pytest --cov app --cov-report html app/tests`. This will execue all the test files and show the results. You can open up the `index.html` file in the `htmlcov` directory to see the coverage report. 

* (11/28/22) As of commit `794d795`, coverage is at 94%.

## Frameworks and Libraries

+ [Stripe](https://stripe.com/docs)
+ [FastAPI](https://fastapi.tiangolo.com)
+ [FastAPI Pagination](https://github.com/uriyyo/fastapi-pagination)
+ [Pydantic](https://pydantic-docs.helpmanual.io)
+ [SQLAlchemy](https://docs.sqlalchemy.org/en/14/intro.html)
