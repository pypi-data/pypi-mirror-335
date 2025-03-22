import os
from typing import List, Optional
from pydantic_settings import BaseSettings 
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with defaults."""
    
    VERSION: str = "1.0.0"
    BACKEND_CORS_ORIGINS: List[str] = []


    PROJECT_PATH: str = Field(default=os.getcwd(), env="PROJECT_PATH")
    
    
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI Auto-Documentation"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    
    DEFAULT_EXCLUDED_DIRS: List[str] = [
        "__pycache__", 
        ".git", 
        ".venv", 
        "venv", 
        "env", 
        "node_modules",
        ".pytest_cache",
        ".mypy_cache",
        "__pypackages__"
    ]
    DEFAULT_EXCLUDED_FILES: List[str] = [
        ".DS_Store",
        ".gitignore",
        "*.pyc",
        "*.pyo",
        "*.pyd"
    ]
    
    
    INCLUDE_PRIVATE_MEMBERS: bool = False
    PARSE_DOCSTRINGS: bool = True
    DEFAULT_OUTPUT_DIR: str = "docs"
    
    
    DEFAULT_WATCH_INTERVAL: int = 1  
    
    # Authentication (??)
    REQUIRE_AUTH: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
