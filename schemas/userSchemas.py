from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    user_id: int = Field(ge=1)
    queries_chat_gpt: int = Field(ge=1, default=3)
    queries_img: int = Field(ge=1, default=1)
    subscription_id: int = Field(ge=1, default=1)


class UserInDBSchema(UserSchema):
    id: int = Field(ge=1)
