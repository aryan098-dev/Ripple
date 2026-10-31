
from fastapi import FastAPI

app = FastAPI(
    title="Ripple API",
    description="Change Impact Intelligence Engine",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "project": "Ripple",
        "message": "Change Impact Intelligence API is running!",
        "status": "online",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Ripple API",
    }
