
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ripple.engine import run_ripple

PROJECT_ROOT = Path(__file__).resolve().parents[1]

app = FastAPI(
    title="Ripple API",
    description="Change Impact Intelligence Engine",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
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


@app.post("/analyze")
def analyze_repository():
    try:
        results = run_ripple(str(PROJECT_ROOT))
        return results

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(error)}",
        )
