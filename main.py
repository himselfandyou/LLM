"""
Main Application Entry Point

FastAPI application for the MCP Server.
"""

import uvicorn
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
from contextlib import asynccontextmanager

from mcp_server.core.config import get_settings
from mcp_server.api.routes import models, inference, health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting MCP Server...")
    logger.info(f"Server configuration: {settings.host}:{settings.port}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Initialize services here if needed
    yield
    
    # Shutdown
    logger.info("Shutting down MCP Server...")

# Create FastAPI application
app = FastAPI(
    title="MCP Server",
    description="Model Context Protocol Server for Language Models",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(models.router, prefix="/api/v1/models", tags=["models"])
app.include_router(inference.router, prefix="/api/v1/inference", tags=["inference"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "MCP Server is running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# API info endpoint
@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "name": "MCP Server",
        "version": "1.0.0",
        "description": "Model Context Protocol Server for Language Models",
        "endpoints": {
            "health": "/health",
            "models": "/api/v1/models",
            "inference": "/api/v1/inference",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )