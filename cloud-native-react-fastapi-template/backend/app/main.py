from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
            "hello": "/api/hello"
        }
    }

@app.get("/api/hello")
async def say_hello():
    return {"message": "Hello from FastAPI"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
