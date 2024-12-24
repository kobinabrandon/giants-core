import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

from general.paths import set_module_root 


class GeneralConfig(BaseSettings):
    """
    Contains various secrets that relate to functionality that pertain to the "general"
    module.

    Attributes: 
        env_file_path: the absolute path to our .env file 
        env_file_found: a boolean that reveals whether the .env file exists or not 
        dropbox_access_token: the access token to my dropbox account
    """
    general_root: Path = set_module_root(from_scratch=False, general=True)
    env_file_path: str = f"{general_root.parent.resolve()}/.env"
    env_file_found: bool =  load_dotenv(find_dotenv(filename=env_file_path))

    assert env_file_found, "There is no .env file"

    _ = SettingsConfigDict(env_file=f"{env_file_path}", env_file_encoding="utf-8")
    dropbox_access_token: str = os.environ["DROPBOX_ACCESS_TOKEN"]
        
general_config = GeneralConfig()

