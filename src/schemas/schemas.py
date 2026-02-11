from pydantic import BaseModel, Field, EmailStr


class UserIn(BaseModel):
    id: int | None = None
    username: str = Field(min_length=3, max_length=200, examples=['john'])
    email: EmailStr = Field(examples=['myemail@email.com'])
    password: str = Field(min_length=8, max_length=200, examples=['mysecretpwd123'])


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
