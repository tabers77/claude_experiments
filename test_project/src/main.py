"""
Minimal FastAPI application for Claude Code learning exercises.
"""
from fastapi import FastAPI
from src.api.routes import router

app = FastAPI(
    title="Minimal API",
    description="A simple API for practicing Claude Code features",
    version="0.1.0"
)

app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Minimal API is running"}
