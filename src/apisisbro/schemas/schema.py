from pydantic import BaseModel, EmailStr


class User(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    username: str
    email: EmailStr
    id: int
