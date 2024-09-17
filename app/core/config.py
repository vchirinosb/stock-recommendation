from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    """
    Cargar variables de entorno desde archivo .env.

    Attributes:
        base_url (str): URL base de API.
    """

    base_url: str = Field(..., description="URL base de la API")
    langchain_tracing_v2: bool = Field(..., description="")
    langchain_endpoint: str = Field(..., description="")
    langchain_api_key: str = Field(..., description="")
    langchain_project: str = Field(..., description="")

    class Config:
        env_file = ".env"


settings = Settings()
