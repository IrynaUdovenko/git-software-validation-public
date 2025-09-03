from pydantic import BaseModel, EmailStr, constr
from datetime import datetime

class UserCreate(BaseModel):
    name: constr(strip_whitespace=True, min_length=1, max_length=50) # type: ignore
    email: EmailStr
    password: constr(strip_whitespace=True, min_length=8, max_length=128) # type: ignore

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    last_login: datetime | None = None

    class Config:
        orm_mode=True

class UserLogin(BaseModel):
    email: EmailStr
    password: constr(strip_whitespace=True, min_length=8, max_length=128) # type: ignore