"""
Configuration Management

Centralized configuration management for the MCP Server using Pydantic settings.
"""

from pydantic import BaseSettings, Field
from typing import Optional, List
import os
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings."""
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    reload: bool = Field(default=False, env="RELOAD")
    
    # Database Configuration
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # Redis Configuration
    redis_url: Optional[str] = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Model Configuration
    model_cache_dir: str = Field(default="./models", env="MODEL_CACHE_DIR")
    default_model: str = Field(default="gpt2", env="DEFAULT_MODEL")
    max_model_size_gb: int = Field(default=10, env="MAX_MODEL_SIZE_GB")
    
    # Security Configuration
    secret_key: str = Field(default="your-secret-key-change-this", env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # CORS Configuration
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")
    
    # Model Management
    enable_model_management: bool = Field(default=True, env="ENABLE_MODEL_MANAGEMENT")
    enable_fine_tuning: bool = Field(default=True, env="ENABLE_FINE_TUNING")
    enable_batch_inference: bool = Field(default=True, env="ENABLE_BATCH_INFERENCE")
    
    # Monitoring Configuration
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    # WebSocket Configuration
    enable_websockets: bool = Field(default=True, env="ENABLE_WEBSOCKETS")
    websocket_ping_interval: int = Field(default=20, env="WEBSOCKET_PING_INTERVAL")
    websocket_ping_timeout: int = Field(default=20, env="WEBSOCKET_PING_TIMEOUT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

# Create settings instance
settings = get_settings()