from pydantic import BaseModel
from typing import Optional


class Settings(BaseModel):
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "Event_Management"

    # JWT settings
    SECRET_KEY: str = "1234"  #
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1

    # class Config:
    #     env_file = ".env"


settings = Settings()