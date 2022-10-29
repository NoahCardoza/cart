from pydantic import BaseModel, Field


class UserContext(BaseModel):
    id: int = Field(..., description="The id of the user", example=1)
    firstname: str = Field(...,
                           description="The firstname of the user", example="John")
    lastname: str = Field(...,
                          description="The lastname of the user", example="Doe")
    email: str = Field(..., description="The email of the user",
                       example="john.doe@gmail.com")
    is_superuser: bool = Field(...,
                               description="Whether the user is a superuser", example=False)
    is_employee: bool = Field(...,
                              description="Whether the user is an employee", example=False)
