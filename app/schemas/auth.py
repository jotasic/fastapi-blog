from pydantic import BaseModel, ConfigDict, EmailStr

from app.constants import EmailVerificationAction  # noqa: TC001


class SendCodeRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    email: EmailStr
    action: EmailVerificationAction


class VerifyCodeRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    email: EmailStr
    action: EmailVerificationAction
    code: str


class VerificationCodeBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    email: EmailStr
    action: EmailVerificationAction

    @property
    def key(self) -> str:
        return f"auth:verification:{self.action}:{self.email}"


class VerificationCodeCreate(VerificationCodeBase):
    code: str


class VerificationCodeRead(VerificationCodeBase):
    pass
