from pydantic import BaseModel, EmailStr, Field


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=200, examples=['john'])
    email: EmailStr = Field(examples=['myemail@email.com'])
    # model_config = ConfigDict(from_attributes=True)


class UserIn(UserSchema):
    password: str = Field(min_length=8, max_length=200, examples=['mysecretpwd123'])


class UserOut(UserSchema):
    id: int


class UserList(BaseModel):
    users: list[UserOut]
