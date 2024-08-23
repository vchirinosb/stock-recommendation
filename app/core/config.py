from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    """
    Cargar variables de entorno desde archivo .env.

    Attributes:
        base_url (str): URL base de API.
    """

    base_url: str = Field(..., description="URL base de la API")

    class Config:
        env_file = ".env"


settings = Settings()
