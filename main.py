from fastapi import FastAPI, Form
from routes.auth import router as auth_router
from db_models.database import Base, engine
from db_models import user, social
from routes.posts import router as posts_router
from routes.comments import router as comment_router
from routes.likes import router as like_router
from routes.profile import router as profile_router
from routes.saved import router as save_router
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Allowed frontend origins
    allow_credentials=True,           # Allows cookies, auth headers
    allow_methods=["*"],              # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],              # Allows all headers (Authorization, Content-Type, etc.)
)





app.include_router(auth_router, prefix="/auth")

app.include_router(posts_router, prefix="/posts")

app.include_router(comment_router, prefix="/comments")

app.include_router(like_router, prefix="/likes")

app.include_router(profile_router, prefix="/profile")

app.include_router(save_router, prefix="/saved")