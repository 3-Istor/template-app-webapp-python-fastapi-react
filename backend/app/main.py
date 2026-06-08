from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import check_database_connection, is_database_enabled

settings = get_settings()
app = FastAPI(title="Cloud Native Template API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur l'API Cloud Native Template",
        "version": "1.0.0",
        "endpoints": {
            "hello": "/api/hello",
            "database": "/api/db/status",
        },
    }


@app.get("/api/hello")
async def say_hello():
    return {"message": "Hello from FastAPI"}


@app.get("/api/db/status")
async def database_status():
    enabled = is_database_enabled()
    return {
        "enabled": enabled,
        "type": settings.db_type if enabled else None,
        "connected": check_database_connection() if enabled else False,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
