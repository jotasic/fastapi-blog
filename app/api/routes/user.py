from fastapi import APIRouter, HTTPException, status

from app import crud
from app.api.deps import AuthUserDep, SessionDep  # noqa: TCH001
from app.schemas import UserCreate, UserRead, UserRegister, UserUpdateMe

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(session: SessionDep, user_register: UserRegister):
    email = user_register.email
    if crud.get_user_by_email(session=session, email=email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_in = UserCreate(**user_register.model_dump())
    return crud.create_user(session=session, user_in=user_in)


@router.get("/me", response_model=UserRead)
async def get_user_me(user: AuthUserDep):
    return user


@router.patch("/me", response_model=UserRead)
async def update_user_me(session: SessionDep, user_in: UserUpdateMe, user: AuthUserDep):
    user_data = user_in.model_dump(exclude_unset=True)
    user.update_from_dict(user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
