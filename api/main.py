from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from api.routes.user import router as users_router
from api.db import engine, Base, get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from contextlib import asynccontextmanager
from utils.exceptions import AppError

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # create all tables (if not exist)
        await conn.run_sync(Base.metadata.create_all)
    yield  

app = FastAPI(lifespan=lifespan)

app.include_router(users_router)

@app.exception_handler(AppError)
async def app_error_handler(request, exc: AppError):
    # TODO add logger and use request parameter for details
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

@app.get("/health")
async def health(db: AsyncSession = Depends(get_session)):
    try:
        await db.execute(text("SELECT 1"))
        return {"database": "ok"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")