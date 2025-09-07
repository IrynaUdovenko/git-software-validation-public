from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from api.schemas.users import UserCreate, UserResponse, UserLogin
from api.schemas.auth import TokenResponse
from api.crud.user import create_user, authenticate_user, get_current_user, update_last_login
from api.db import get_session
from api.utils.token_utils import create_access_token

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

# gets token from header or returns None if no header
auth_scheme = HTTPBearer(auto_error=False)

# registers user
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_session)):
    return await create_user(user_in, db)

# gets token 
@router.post("/login", response_model=TokenResponse)
async def login_user(credentials: UserLogin, db: AsyncSession = Depends(get_session)):
    user = await authenticate_user(credentials.email, credentials.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    await update_last_login(user.id, db)

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

#get user
@router.get("/me", response_model=UserResponse)
async def get_user_details(creds: HTTPAuthorizationCredentials | None = Depends(auth_scheme), db: AsyncSession = Depends(get_session)):
    if creds is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = creds.credentials
    user = await get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
