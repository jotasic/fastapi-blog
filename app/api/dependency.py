from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import verify_access_token
from app.models import User

if TYPE_CHECKING:
    from app.database import SessionDep

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")
TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user(*, session: SessionDep, token: TokenDep):
    data = verify_access_token(token)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = session.get(User, data["sub"])
    return user


AuthUserDep = Annotated[User, Depends(get_current_user)]
