from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(..., description="The access token for the user")
    token_type: str = Field(..., description="The type of token")
