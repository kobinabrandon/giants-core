import os
from dotenv import load_dotenv, find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


_ = load_dotenv(find_dotenv())


class GeneralConfig(BaseSettings):
    _ = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    dropbox_access_token: str = os.environ["DROPBOX_ACCESS_TOKEN"]

general_config = GeneralConfig()

