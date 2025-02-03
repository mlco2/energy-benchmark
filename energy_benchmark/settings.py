from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    llama_cpp_load_options: Optional[dict]

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra="allow")


settings = Settings()