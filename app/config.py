from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # JSON completo de la cuenta de servicio de Google Earth Engine (como texto,
    # ej. pegando el contenido del archivo .json descargado de Google Cloud)
    EE_SERVICE_ACCOUNT_JSON: str = ""
    EE_PROJECT_ID: str = ""

    # Bounding box del área de interés (Campo Rubiales, Puerto Gaitán, Meta)
    AOI_LON_MIN: float = -71.70
    AOI_LAT_MIN: float = 3.55
    AOI_LON_MAX: float = -71.10
    AOI_LAT_MAX: float = 3.95

    class Config:
        env_file = ".env"


settings = Settings()
