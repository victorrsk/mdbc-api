from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    DATABASE_URL: str = ''
    SECRET_KEY: str = ''
    TOKEN_ALGORITHM: str = ''
    TOKEN_MINUTES_EXPIRE_TIME: int = 0
    MAIL_PASSWORD: str = ''
    MAIL_FROM: str = ''
    TEST_FLAG: int = 0
