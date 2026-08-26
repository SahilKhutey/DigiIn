from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import Base, engine
from app.models import entities
from app.api.v1 import auth, citizen, proofs, government, health, documents, review, jobs
from app.core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="DigiLocker X development foundation"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(citizen.router, prefix="/api/v1")
app.include_router(proofs.router, prefix="/api/v1")
app.include_router(government.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(review.router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": "0.2.0",
        "status": "running",
        "docs": "/docs",
    }

app.include_router(jobs.router, prefix='/api/v1')
