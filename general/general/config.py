import torch
from pydantic_settings import BaseSettings


class GeneralConfig(BaseSettings):
    device: torch.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


general_config = GeneralConfig

