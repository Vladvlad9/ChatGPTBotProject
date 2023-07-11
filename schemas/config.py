from pydantic import BaseModel


class BotSchema(BaseModel):
    TOKEN: str
    ADMINS: list[int]


class OpenAISchema(BaseModel):
    KEY: str


class HelpSchema(BaseModel):
    TechnicalSupport: str
    AdvertisingOtherIssues: str


class ChannelSchema(BaseModel):
    CHANNEL_ID: str
    CHANNEL_NAME: str


class ConfigSchema(BaseModel):
    BOT: BotSchema
    CHANNEL: ChannelSchema
    OpenAI: OpenAISchema
    HELP: HelpSchema

    DATABASE: str
