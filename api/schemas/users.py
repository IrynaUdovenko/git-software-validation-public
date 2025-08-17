from pydantic import BaseModel, EmailStr, constr
from typing import Annotated

class UserCreate(BaseModel):
    name: Annotated[str,constr(strip_whitespace=True, min_length=1, max_length=50)]
    email: EmailStr
    password: Annotated[str,constr(strip_whitespace=True, min_length=8, max_length=128)]

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True
