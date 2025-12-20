from fastapi import APIRouter

from app.constants import APITagName

from .routes import auth, post, post_comment, user

api_v1_router = APIRouter()

api_v1_router.include_router(auth.router, prefix="/auth", tags=[APITagName.AUTH])
api_v1_router.include_router(user.router, prefix="/user", tags=[APITagName.USER])
api_v1_router.include_router(post.router, prefix="/posts", tags=[APITagName.POST])
api_v1_router.include_router(post_comment.router, prefix="/post-comments", tags=[APITagName.POST])
