from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database Settings
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    
    # LLM Settings
    GROQ_API_KEY: str

    class Config:
        env_file = '.env'
    
settings = Settings()