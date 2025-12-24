from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm  # noqa: TCH002

from app import crud
from app.api.deps import SessionDep  # noqa: TCH001
from app.core.security import create_access_token, verify_password
from app.schemas import BearerAccessToken

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
