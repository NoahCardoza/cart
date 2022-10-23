from app import environ
from fastapi.middleware.cors import CORSMiddleware

allow_origins = []
allow_origin_regex = None

if environ.PRODUCTION:
    # only allow requests from the production frontend
    allow_origins.append("https://www.producegoose.farm")
elif environ.DEVELOPMENT:
    # allow all origins in development
    allow_origins = ["*"]
elif environ.STAGING:
    # allow local frontend development to access staging backend
    allow_origins.append("http://localhost:3000")
    allow_origins.append("http://127.0.0.1:3000")

    # allow the staging frontend to access staging backend
    allow_origins.append("https://produce-goose-frontend-stg.herokuapp.com")

    # allow review apps to access staging backend
    allow_origin_regex = r"https:\/\/produce-goos-.+\.herokuapp\.com"


def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_origin_regex=allow_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
