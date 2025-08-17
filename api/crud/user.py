from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from passlib.context import CryptContext
from sqlalchemy import select
from utils.exceptions import EmailAlreadyExists, DatabaseError

from api.models.users import User
from api.schemas.users import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def create_user(user_data: UserCreate, session: AsyncSession) -> User:
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
        return new_user

    except IntegrityError:
        await session.rollback()
        raise EmailAlreadyExists("User with this email already exists.")

    except SQLAlchemyError:
        await session.rollback()
        raise DatabaseError("Database error occurred.")

async def get_user_by_email(email: str, session: AsyncSession) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()