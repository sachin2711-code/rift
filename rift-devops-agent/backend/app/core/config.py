# # """
# # Configuration settings for the RIFT DevOps Agent
# # """

# # import os
# # from functools import lru_cache
# # from typing import Optional, List

# # from pydantic import Field
# # from pydantic_settings import BaseSettings


# # class Settings(BaseSettings):
# #     """Application settings"""
    
# #     # App
# #     APP_NAME: str = "RIFT DevOps Agent"
# #     APP_VERSION: str = "1.0.0"
# #     DEBUG: bool = Field(default=False, env="DEBUG")
    
# #     # API Keys
# #     OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
# #     GITHUB_TOKEN: str = Field(default="", env="GITHUB_TOKEN")
# #     GITHUB_WEBHOOK_SECRET: str = Field(default="", env="GITHUB_WEBHOOK_SECRET")
    
# #     # Vector DB
# #     VECTOR_DB_TYPE: str = Field(default="chromadb", env="VECTOR_DB_TYPE")  # chromadb or pinecone
# #     CHROMA_DB_PATH: str = Field(default="./chroma_db", env="CHROMA_DB_PATH")
# #     PINECONE_API_KEY: str = Field(default="", env="PINECONE_API_KEY")
# #     PINECONE_ENVIRONMENT: str = Field(default="", env="PINECONE_ENVIRONMENT")
# #     PINECONE_INDEX_NAME: str = Field(default="rift-devops-agent", env="PINECONE_INDEX_NAME")
    
# #     # Database
# #     DATABASE_URL: str = Field(default="sqlite:///./rift_agent.db", env="DATABASE_URL")
    
# #     # Redis (optional, for caching)
# #     REDIS_URL: str = Field(default="", env="REDIS_URL")
    
# #     # Agent Settings
# #     MAX_ITERATIONS: int = Field(default=5, env="MAX_ITERATIONS")
# #     RETRY_DELAY_SECONDS: int = Field(default=30, env="RETRY_DELAY_SECONDS")
# #     SANDBOX_TIMEOUT: int = Field(default=300, env="SANDBOX_TIMEOUT")  # 5 minutes
    
# #     # Code Execution
# #     DOCKER_IMAGE: str = Field(default="python:3.11-slim", env="DOCKER_IMAGE")
# #     ENABLE_SANDBOX: bool = Field(default=True, env="ENABLE_SANDBOX")
    
# #     # Notifications
# #     SLACK_WEBHOOK_URL: str = Field(default="", env="SLACK_WEBHOOK_URL")
# #     DISCORD_WEBHOOK_URL: str = Field(default="", env="DISCORD_WEBHOOK_URL")
    
# #     # CORS
# #     CORS_ORIGINS: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    
# #     # Logging
# #     LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
# #     LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
# #     # Paths
# #     REPOSITORIES_PATH: str = Field(default="/tmp/rift-repos", env="REPOSITORIES_PATH")
# #     RESULTS_PATH: str = Field(default="/tmp/rift-results", env="RESULTS_PATH")
    
# #     # GitHub
# #     GITHUB_USERNAME: str = Field(default="", env="GITHUB_USERNAME")
# #     GITHUB_EMAIL: str = Field(default="rift-agent@example.com", env="GITHUB_EMAIL")
    
# #     # LLM Model
# #     LLM_MODEL: str = Field(default="gpt-4-turbo-preview", env="LLM_MODEL")
# #     LLM_TEMPERATURE: float = Field(default=0.1, env="LLM_TEMPERATURE")
    
# #     class Config:
# #         env_file = ".env"
# #         env_file_encoding = "utf-8"


# # @lru_cache()
# # def get_settings() -> Settings:
# #     """Get cached settings instance"""
# #     return Settings()


# # settings = get_settings()
# """
# Configuration settings for the RIFT DevOps Agent
# """

# import os
# from functools import lru_cache
# from typing import Optional, List

# from pydantic import Field
# from pydantic_settings import BaseSettings


# class Settings(BaseSettings):
#     """Application settings"""

#     # App
#     APP_NAME: str = "RIFT DevOps Agent"
#     APP_VERSION: str = "1.0.0"
#     DEBUG: bool = Field(default=False, env="DEBUG")

#     # API Keys
#     OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")

#     # GitHub — server token is now OPTIONAL
#     # If every user logs in via OAuth, this can be left empty
#     GITHUB_TOKEN: str = Field(default="", env="GITHUB_TOKEN")
#     GITHUB_WEBHOOK_SECRET: str = Field(default="", env="GITHUB_WEBHOOK_SECRET")
#     GITHUB_USERNAME: str = Field(default="", env="GITHUB_USERNAME")
#     GITHUB_EMAIL: str = Field(default="rift-agent@example.com", env="GITHUB_EMAIL")

#     # ── GitHub OAuth (NEW) ─────────────────────────────────────────────────
#     GITHUB_CLIENT_ID: str = Field(default="", env="GITHUB_CLIENT_ID")
#     GITHUB_CLIENT_SECRET: str = Field(default="", env="GITHUB_CLIENT_SECRET")
#     FRONTEND_URL: str = Field(default="http://localhost:5173", env="FRONTEND_URL")

#     # Vector DB
#     VECTOR_DB_TYPE: str = Field(default="chromadb", env="VECTOR_DB_TYPE")
#     CHROMA_DB_PATH: str = Field(default="./chroma_db", env="CHROMA_DB_PATH")
#     PINECONE_API_KEY: str = Field(default="", env="PINECONE_API_KEY")
#     PINECONE_ENVIRONMENT: str = Field(default="", env="PINECONE_ENVIRONMENT")
#     PINECONE_INDEX_NAME: str = Field(default="rift-devops-agent", env="PINECONE_INDEX_NAME")

#     # Database
#     DATABASE_URL: str = Field(default="sqlite:///./rift_agent.db", env="DATABASE_URL")

#     # Redis (optional)
#     REDIS_URL: str = Field(default="", env="REDIS_URL")

#     # Agent Settings
#     MAX_ITERATIONS: int = Field(default=5, env="MAX_ITERATIONS")
#     RETRY_DELAY_SECONDS: int = Field(default=30, env="RETRY_DELAY_SECONDS")
#     SANDBOX_TIMEOUT: int = Field(default=300, env="SANDBOX_TIMEOUT")

#     # Code Execution
#     DOCKER_IMAGE: str = Field(default="python:3.11-slim", env="DOCKER_IMAGE")
#     ENABLE_SANDBOX: bool = Field(default=True, env="ENABLE_SANDBOX")

#     # Notifications
#     SLACK_WEBHOOK_URL: str = Field(default="", env="SLACK_WEBHOOK_URL")
#     DISCORD_WEBHOOK_URL: str = Field(default="", env="DISCORD_WEBHOOK_URL")

#     # CORS
#     CORS_ORIGINS: List[str] = Field(default=["*"], env="CORS_ORIGINS")

#     # Logging
#     LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
#     LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")

#     # Paths
#     REPOSITORIES_PATH: str = Field(default="/tmp/rift-repos", env="REPOSITORIES_PATH")
#     RESULTS_PATH: str = Field(default="/tmp/rift-results", env="RESULTS_PATH")

#     # LLM Model
#     LLM_MODEL: str = Field(default="gpt-4-turbo-preview", env="LLM_MODEL")
#     LLM_TEMPERATURE: float = Field(default=0.1, env="LLM_TEMPERATURE")

#     class Config:
#         env_file = ".env"
#         env_file_encoding = "utf-8"


# @lru_cache()
# def get_settings() -> Settings:
#     """Get cached settings instance"""
#     return Settings()


# settings = get_settings()
"""
Configuration settings for the RIFT DevOps Agent
"""

import os
from functools import lru_cache
from typing import Optional, List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # App
    APP_NAME: str = "RIFT DevOps Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")

    # API Keys — switched from OpenAI to Gemini
    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")

    # GitHub — server token is OPTIONAL if users login via OAuth
    GITHUB_TOKEN: str = Field(default="", env="GITHUB_TOKEN")
    GITHUB_WEBHOOK_SECRET: str = Field(default="", env="GITHUB_WEBHOOK_SECRET")
    GITHUB_USERNAME: str = Field(default="", env="GITHUB_USERNAME")
    GITHUB_EMAIL: str = Field(default="rift-agent@example.com", env="GITHUB_EMAIL")

    # GitHub OAuth
    GITHUB_CLIENT_ID: str = Field(default="", env="GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET: str = Field(default="", env="GITHUB_CLIENT_SECRET")
    FRONTEND_URL: str = Field(default="http://localhost:5173", env="FRONTEND_URL")

    # Vector DB
    VECTOR_DB_TYPE: str = Field(default="chromadb", env="VECTOR_DB_TYPE")
    CHROMA_DB_PATH: str = Field(default="./chroma_db", env="CHROMA_DB_PATH")
    PINECONE_API_KEY: str = Field(default="", env="PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: str = Field(default="", env="PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME: str = Field(default="rift-devops-agent", env="PINECONE_INDEX_NAME")

    # Database
    DATABASE_URL: str = Field(default="sqlite:///./rift_agent.db", env="DATABASE_URL")

    # Redis (optional)
    REDIS_URL: str = Field(default="", env="REDIS_URL")

    # Agent Settings
    MAX_ITERATIONS: int = Field(default=5, env="MAX_ITERATIONS")
    RETRY_DELAY_SECONDS: int = Field(default=30, env="RETRY_DELAY_SECONDS")
    SANDBOX_TIMEOUT: int = Field(default=300, env="SANDBOX_TIMEOUT")

    # Code Execution
    DOCKER_IMAGE: str = Field(default="python:3.11-slim", env="DOCKER_IMAGE")
    ENABLE_SANDBOX: bool = Field(default=True, env="ENABLE_SANDBOX")

    # Notifications
    SLACK_WEBHOOK_URL: str = Field(default="", env="SLACK_WEBHOOK_URL")
    DISCORD_WEBHOOK_URL: str = Field(default="", env="DISCORD_WEBHOOK_URL")

    # CORS
    CORS_ORIGINS: List[str] = Field(default=["*"], env="CORS_ORIGINS")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")

    # Paths
    REPOSITORIES_PATH: str = Field(default="/tmp/rift-repos", env="REPOSITORIES_PATH")
    RESULTS_PATH: str = Field(default="/tmp/rift-results", env="RESULTS_PATH")

    # LLM Model — switched to Gemini
    LLM_MODEL: str = Field(default="gemini-2.0-flash", env="LLM_MODEL")
    LLM_TEMPERATURE: float = Field(default=0.1, env="LLM_TEMPERATURE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()