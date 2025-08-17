from fastapi import FastAPI
from api.routes.user import router as users_router

app = FastAPI()

app.include_router(users_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}