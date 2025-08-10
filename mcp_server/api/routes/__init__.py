"""
API Routes Package

Contains all API route handlers for the MCP Server.
"""

from . import models, inference, health

__all__ = [
    "models",
    "inference",
    "health"
]