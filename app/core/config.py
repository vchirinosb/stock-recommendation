from pydantic import BaseSettings


class Settings(BaseSettings):

    """
    Cargar variables de entorno desde archivo .env.

    Attributes:
        base_url (str): URL base de API.
    """

    base_url: str

    class Config:
        env_file = ".env"

settings = Settings()
