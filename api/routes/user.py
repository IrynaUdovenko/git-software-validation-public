from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.schemas.users import UserCreate, UserResponse
from api.crud.user import create_user
from api.db import get_session
from utils.exceptions import EmailAlreadyExists, DatabaseError

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_session)):
    try:
        user = await create_user(user_in, db)
        return user

    except EmailAlreadyExists as e:
        raise HTTPException(status_code=409, detail=str(e))  # 409 Conflict

    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Internal server error")


