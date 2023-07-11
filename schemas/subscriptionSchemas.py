from pydantic import BaseModel, Field


class SubscriptionSchema(BaseModel):
    name: str
    price: str


class SubscriptionInDBSchema(SubscriptionSchema):
    id: int = Field(ge=1)
