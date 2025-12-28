from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi_mail import FastMail, MessageSchema, MessageType

from app import crud
from app.api.deps import AsyncSessionDep, AuthUserDep, SettingDep  # noqa: TCH001
from app.constants import EmailVerificationAction
from app.core.redis_client import RedisAsyncDep  # noqa: TC001
from app.schemas import UserCreate, UserRead, UserRegister, UserUpdateMe, VerificationCodeRead

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    session: AsyncSessionDep,
    cache: RedisAsyncDep,
    settings: SettingDep,
    background_tasks: BackgroundTasks,
    user_register: UserRegister,
):
    email = user_register.email

    code_in = VerificationCodeRead(email=user_register.email, action=EmailVerificationAction.SIGNUP)
    code = await crud.get_verification_code(cache, code_in)

    if user_register.verification_code != code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    if await crud.get_user_by_email(session=session, email=email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_in = UserCreate(**user_register.model_dump())
    user_db = await crud.create_user(session=session, user_in=user_in)

    data = {
        "nickname": user_db.nickname,
    }

    message = MessageSchema(
        subject="가입을 진심으로 축합니다", recipients=[user_db.email], template_body=data, subtype=MessageType.html
    )
    fm = FastMail(settings.EMAIL)
    background_tasks.add_task(fm.send_message, message, template_name="system_mail/welcome.html")

    return user_db


@router.get("/me", response_model=UserRead)
async def get_user_me(user: AuthUserDep):
    return user


@router.patch("/me", response_model=UserRead)
async def update_user_me(session: AsyncSessionDep, user_in: UserUpdateMe, user: AuthUserDep):
    user_data = user_in.model_dump(exclude_unset=True)
    user.update_from_dict(user_data)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
