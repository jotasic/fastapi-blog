from pydantic import BaseModel, Field


class BearerAccessToken(BaseModel):
    access_token: str
    token_type: str = Field(default="Bearer", frozen=True)
