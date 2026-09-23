# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import analyze
app = FastAPI(title="Cyberbullying Analyzer API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # depois trocar pelo domínio final
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(analyze.router, prefix="/api")
@app.get("/")
def health_check():
    return {"status": "ok"}