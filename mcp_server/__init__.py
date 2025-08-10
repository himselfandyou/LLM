"""
MCP Server (Model Context Protocol)

A comprehensive server implementation for serving language models and
providing a RESTful API for model inference and management.
"""

__version__ = "1.0.0"
__author__ = "MCP Development Team"

from .core.config import get_settings
from .api.routes import models, inference, health

__all__ = [
    "get_settings",
    "models",
    "inference", 
    "health"
]