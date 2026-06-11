from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import auth, student, training, assessment, comment, promotion

app = FastAPI(title="青少年体育训练档案平台", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(student.router)
app.include_router(training.router)
app.include_router(assessment.router)
app.include_router(comment.router)
app.include_router(promotion.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"code": 0, "data": {"name": "青少年体育训练档案平台", "version": "1.0.0"}, "message": "success"}
