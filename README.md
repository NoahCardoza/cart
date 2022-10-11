# Product Goose (Backend)

A group project for CMPE 131 at SJSU.

## Setup

To run the project, you need to have `python 3.9` and `pipenv` installed.

If you don't have `pipenv`, you can install it by running `python -m pip install pipenv`.

Then, run `python -m pipenv install` to install all the dependencies.

When you are done, run `python -m pipenv run uvicorn app:serve --reload` to run the project.

## API Documentation

The API documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and 
[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc). They both show the same information but 
in slightly different ways formats.

## Frameworks and Libraries

+ [FastAPI](https://fastapi.tiangolo.com/)
+ [Pydantic](https://pydantic-docs.helpmanual.io/)
