from fastapi import FastAPI

from backend.core.logging import setup_logging
from backend.routers import analyze

setup_logging()
app = FastAPI(title="YouTube Moderation API", version="1.1.0")

app.include_router(analyze.router)


@app.get("/health")
def health():
    return {"status": "ok"}