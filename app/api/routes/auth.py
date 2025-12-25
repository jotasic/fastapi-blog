import string
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm  # noqa: TCH002
from fastapi_mail import FastMail, MessageSchema, MessageType
from nanoid import generate

from app import crud
from app.api.deps import SessionDep  # noqa: TCH001
from app.constants import EmailVerificationAction
from app.core.config import settings
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
async def send_verification_code(
    session: SessionDep, cache: RedisAsyncDep, background_tasks: BackgroundTasks, request: SendCodeRequest
):
    user = crud.get_user_by_email(session=session, email=request.email)

    match request.action:
        case EmailVerificationAction.SIGNUP if not user:
            code = generate(string.digits, size=6)
            code_in = VerificationCodeCreate(**request.model_dump(), code=code)
            await crud.create_verification_code(cache=cache, code_in=code_in)

            data = {
                "title": "회원가입 인증 코드",
                "verification_code": code,
            }

            message = MessageSchema(
                subject=data["title"], recipients=[request.email], template_body=data, subtype=MessageType.html
            )
            fm = FastMail(settings.EMAIL)
            background_tasks.add_task(fm.send_message, message, template_name="system_mail/verification_code.html")
            return {"Code": "OK"}

        case _:
            raise HTTPException(status_code=400, detail="Invalid")
