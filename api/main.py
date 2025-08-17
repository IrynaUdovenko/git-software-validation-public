from fastapi import FastAPI
from api.routes.user import router as users_router
from api.db import engine, Base
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(users_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}