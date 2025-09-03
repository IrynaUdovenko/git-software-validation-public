from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from api.utils.auth_utils import hash_password, validate_password
from api.utils.token_utils import decode_access_token
from sqlalchemy import select, update
from utils.exceptions import EmailAlreadyExists, DatabaseError, DatabaseUnavailable
from datetime import datetime, timezone

from api.models.users import User
from api.schemas.users import UserCreate
from api.schemas.users import UserResponse

async def create_user(user_data: UserCreate, session: AsyncSession) -> UserResponse:
    hashed_password = hash_password(user_data.password)

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password
    )

    try:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return UserResponse.from_orm(new_user)

    except IntegrityError as e:
        raise EmailAlreadyExists() from e

    except OperationalError as e:
        raise DatabaseUnavailable() from e

    except SQLAlchemyError as e:
        raise DatabaseError() from e

    finally:
        if session.in_transaction():
            await session.rollback()

async def authenticate_user(email: str, password: str, session: AsyncSession) -> UserResponse | None:
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not validate_password(password, user.hashed_password):
        return None

    return UserResponse.from_orm(user) 

async def get_current_user(token: str, session: AsyncSession = AsyncSession) -> UserResponse | None:
    email = decode_access_token(token)
    
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    return UserResponse.from_orm(user) if user else None

async def update_last_login(user_id: int, session: AsyncSession):
    try:
        stmt = update(User).where(User.id == user_id).values(last_login=datetime.now(timezone.utc))
        await session.execute(stmt)
        await session.commit()
    except SQLAlchemyError as e:
        raise DatabaseError from e
    finally:
        if session.in_transaction():
            await session.rollback()
        
