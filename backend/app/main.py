from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter

from app import telemetry
from app.config import get_settings
from app.database import check_database_connection, is_database_enabled

telemetry.configure_logging()

settings = get_settings()
app = FastAPI(title="Cloud Native Template API", telemetry=telemetry.configure_tracing())
telemetry.instrument(app)

# Example business metric, exposed on /metrics as app_greetings_total. Keep
# label values to a small fixed set: never a user id, a name or a raw path.
GREETINGS = Counter("app_greetings", "Greetings served by the API.")

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
            "health": "/health",
        },
    }


@app.get("/api/hello")
async def say_hello():
    GREETINGS.inc()
    return {"message": "Hello from FastAPI"}


@app.get("/api/hello/{name}")
async def say_hello_to(name: str):
    GREETINGS.inc()
    return {"message": f"Hello {name} from FastAPI"}


@app.get("/api/db/status")
async def database_status():
    enabled = is_database_enabled()
    return {
        "enabled": enabled,
        "type": settings.db_type if enabled else None,
        "connected": check_database_connection() if enabled else False,
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
