from fastapi import FastAPI
from app.database import Base, engine
from app import models  # noqa: F401  (ensures models are registered before create_all)
from app.auth import router as auth_router
from app.predict import router as predict_router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.password_reset import router as password_reset_router
from app.history import router as history_router
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="COCKATOOS API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Create tables
Base.metadata.create_all(bind=engine)
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(predict_router, tags=["Prediction"])
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(password_reset_router, prefix="/auth", tags=["Password Reset"])
app.include_router(history_router, prefix="/api", tags=["History"])
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def root():
    return {"message": "API Running"}

   