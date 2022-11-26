from pydantic import BaseModel, EmailStr, Field


class NewUserIn(BaseModel):
    firstname: str = Field(..., description="The first name of the user")
    lastname: str = Field(..., description="The last name of the user")
    username: EmailStr = Field(..., description="The username of user")
    password: str = Field(..., description="The password of the user", min_length=8, max_length=32)


class UserContext(BaseModel):
    id: int = Field(..., description="The id of the user", example=1)
    stripe_id: str = Field(..., description="The id of the user in stripe", example="cus_MrTJhD1j3KQwTX")
    
    firstname: str = Field(..., description="The firstname of the user", example="John")
    lastname: str = Field(..., description="The lastname of the user", example="Doe")
    email: EmailStr = Field(..., description="The email of the user", example="john.doe@gmail.com")
    is_superuser: bool = Field(..., description="Whether the user is a superuser", example=False)
    is_employee: bool = Field(..., description="Whether the user is an employee", example=False)

    exp: int = Field(..., description="The expiary date epoch timestamp of the user", example="1669315959")
