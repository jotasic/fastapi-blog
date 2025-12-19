from fastapi import APIRouter

from app.constants import APITagName

from .routes import auth, post, user

api_v1_router = APIRouter()

api_v1_router.include_router(auth.router, prefix="/auth", tags=[APITagName.AUTH])
api_v1_router.include_router(user.router, prefix="/user", tags=[APITagName.USER])
api_v1_router.include_router(post.router, prefix="/posts", tags=[APITagName.POST])
