"""
Model Management API Routes

API endpoints for managing models in the MCP Server.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import uuid
from datetime import datetime

from ...core.database import ModelRegistryManager, DatabaseManager
from ...core.config import get_settings
from ...services.model_service import ModelService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/models", tags=["models"])

# Pydantic models for request/response
class ModelCreateRequest(BaseModel):
    model_name: str
    model_type: str
    model_path: str
    version: Optional[str] = "1.0.0"
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class ModelUpdateRequest(BaseModel):
    model_name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None

class ModelResponse(BaseModel):
    model_id: str
    model_name: str
    model_type: str
    model_path: str
    version: str
    description: Optional[str]
    parameters: Optional[Dict[str, Any]]
    metrics: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class ModelListResponse(BaseModel):
    models: List[ModelResponse]
    total: int
    page: int
    size: int

# Dependency injection
def get_model_service():
    """Get model service instance."""
    settings = get_settings()
    db_manager = DatabaseManager(settings.database_url or "sqlite:///./mcp_server.db")
    model_registry = ModelRegistryManager(db_manager)
    return ModelService(model_registry)

@router.get("/", response_model=ModelListResponse)
async def list_models(
    model_type: Optional[str] = None,
    active_only: bool = True,
    page: int = 1,
    size: int = 20,
    model_service: ModelService = Depends(get_model_service)
):
    """
    List all registered models.
    
    Args:
        model_type: Filter by model type
        active_only: Show only active models
        page: Page number for pagination
        size: Number of models per page
        model_service: Model service instance
        
    Returns:
        List of models with pagination info
    """
    try:
        models = model_service.list_models(
            model_type=model_type,
            active_only=active_only,
            page=page,
            size=size
        )
        
        return ModelListResponse(
            models=[ModelResponse.from_orm(model) for model in models["models"]],
            total=models["total"],
            page=page,
            size=size
        )
        
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list models"
        )

@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: str,
    model_service: ModelService = Depends(get_model_service)
):
    """
    Get model details by ID.
    
    Args:
        model_id: Model identifier
        model_service: Model service instance
        
    Returns:
        Model details
    """
    try:
        model = model_service.get_model(model_id)
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model {model_id} not found"
            )
        
        return ModelResponse.from_orm(model)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model {model_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get model"
        )

@router.post("/", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def register_model(
    request: ModelCreateRequest,
    model_service: ModelService = Depends(get_model_service)
):
    """
    Register a new model.
    
    Args:
        request: Model creation request
        model_service: Model service instance
        
    Returns:
        Registered model details
    """
    try:
        # Generate unique model ID
        model_id = str(uuid.uuid4())
        
        model = model_service.register_model(
            model_id=model_id,
            model_name=request.model_name,
            model_type=request.model_type,
            model_path=request.model_path,
            version=request.version,
            description=request.description,
            parameters=request.parameters
        )
        
        return ModelResponse.from_orm(model)
        
    except Exception as e:
        logger.error(f"Error registering model: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register model"
        )

@router.put("/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: str,
    request: ModelUpdateRequest,
    model_service: ModelService = Depends(get_model_service)
):
    """
    Update model details.
    
    Args:
        model_id: Model identifier
        request: Model update request
        model_service: Model service instance
        
    Returns:
        Updated model details
    """
    try:
        model = model_service.update_model(
            model_id=model_id,
            model_name=request.model_name,
            description=request.description,
            parameters=request.parameters,
            metrics=request.metrics
        )
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model {model_id} not found"
            )
        
        return ModelResponse.from_orm(model)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating model {model_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update model"
        )

@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: str,
    model_service: ModelService = Depends(get_model_service)
):
    """
    Delete a model.
    
    Args:
        model_id: Model identifier
        model_service: Model service instance
    """
    try:
        success = model_service.delete_model(model_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model {model_id} not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting model {model_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete model"
        )

@router.get("/{model_id}/metrics")
async def get_model_metrics(
    model_id: str,
    model_service: ModelService = Depends(get_model_service)
):
    """
    Get model performance metrics.
    
    Args:
        model_id: Model identifier
        model_service: Model service instance
        
    Returns:
        Model metrics
    """
    try:
        model = model_service.get_model(model_id)
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model {model_id} not found"
            )
        
        return {
            "model_id": model_id,
            "metrics": model.metrics or {},
            "last_updated": model.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metrics for model {model_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get model metrics"
        )

@router.post("/{model_id}/metrics")
async def update_model_metrics(
    model_id: str,
    metrics: Dict[str, Any],
    model_service: ModelService = Depends(get_model_service)
):
    """
    Update model performance metrics.
    
    Args:
        model_id: Model identifier
        metrics: New metrics data
        model_service: Model service instance
        
    Returns:
        Success status
    """
    try:
        success = model_service.update_model_metrics(model_id, metrics)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model {model_id} not found"
            )
        
        return {"message": "Metrics updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating metrics for model {model_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update model metrics"
        )

@router.get("/types", response_model=List[str])
async def get_model_types(
    model_service: ModelService = Depends(get_model_service)
):
    """
    Get list of available model types.
    
    Args:
        model_service: Model service instance
        
    Returns:
        List of model types
    """
    try:
        return model_service.get_model_types()
        
    except Exception as e:
        logger.error(f"Error getting model types: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get model types"
        )