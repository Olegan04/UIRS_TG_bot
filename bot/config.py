from os import getenv
from pathlib import Path

from pydantic import BaseModel, SecretStr, PostgresDsn
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    bot_token: SecretStr
    db_url: PostgresDsn

def parse_settings() -> Settings:
    return Settings()