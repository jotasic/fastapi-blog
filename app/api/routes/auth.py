import string
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm  # noqa: TCH002
from nanoid import generate

from app import crud
from app.api.deps import SessionDep  # noqa: TCH001
from app.constants import EmailVerificationAction
from app.core.redis_client import RedisAsyncDep  # noqa: TC001
from app.core.security import create_access_token, verify_password
from app.schemas import BearerAccessToken, SendCodeRequest, VerificationCodeCreate

router = APIRouter()


@router.post("/login", response_model=BearerAccessToken)
async def login(*, session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = crud.get_user_by_email(session=session, email=form_data.username)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token = create_access_token(sub=str(user.id), data={"id": user.id})

    bearer_access_token = BearerAccessToken(access_token=access_token)
    return bearer_access_token


@router.post("/send-code", status_code=status.HTTP_202_ACCEPTED)
async def send_verification_code(session: SessionDep, cache: RedisAsyncDep, request: SendCodeRequest):
    user = crud.get_user_by_email(session=session, email=request.email)

    match request.action:
        case EmailVerificationAction.SIGNUP if not user:
            code_in = VerificationCodeCreate(**request.model_dump(), code=generate(string.digits, size=6))
            await crud.create_verification_code(cache=cache, code_in=code_in)
            return {"Code": "OK"}
        case _:
            raise HTTPException(status_code=400, detail="Invalid")
