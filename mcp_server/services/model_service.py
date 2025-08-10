"""
Model Service

Business logic for model management operations.
"""

from typing import List, Optional, Dict, Any
import logging
import os
from datetime import datetime

from ..core.database import ModelRegistryManager, ModelRegistry

logger = logging.getLogger(__name__)

class ModelService:
    """Service for model management operations."""
    
    def __init__(self, model_registry: ModelRegistryManager):
        """Initialize model service."""
        self.model_registry = model_registry
    
    def register_model(
        self,
        model_id: str,
        model_name: str,
        model_type: str,
        model_path: str,
        version: str = "1.0.0",
        description: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ModelRegistry:
        """Register a new model."""
        try:
            # Validate model path exists
            if not os.path.exists(model_path):
                raise ValueError(f"Model path does not exist: {model_path}")
            
            # Validate model type
            valid_types = ["text-generation", "classification", "ner", "qa", "summarization"]
            if model_type not in valid_types:
                raise ValueError(f"Invalid model type. Must be one of: {valid_types}")
            
            # Register model
            model = self.model_registry.register_model(
                model_id=model_id,
                model_name=model_name,
                model_type=model_type,
                model_path=model_path,
                version=version,
                description=description,
                parameters=parameters
            )
            
            logger.info(f"Model {model_id} registered successfully")
            return model
            
        except Exception as e:
            logger.error(f"Error registering model {model_id}: {str(e)}")
            raise
    
    def get_model(self, model_id: str) -> Optional[ModelRegistry]:
        """Get model by ID."""
        try:
            return self.model_registry.get_model(model_id)
        except Exception as e:
            logger.error(f"Error getting model {model_id}: {str(e)}")
            raise
    
    def list_models(
        self,
        model_type: Optional[str] = None,
        active_only: bool = True,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """List models with pagination."""
        try:
            models = self.model_registry.list_models(
                model_type=model_type,
                active_only=active_only
            )
            
            # Apply pagination
            total = len(models)
            start_idx = (page - 1) * size
            end_idx = start_idx + size
            paginated_models = models[start_idx:end_idx]
            
            return {
                "models": paginated_models,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
            
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            raise
    
    def update_model(
        self,
        model_id: str,
        model_name: Optional[str] = None,
        description: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None
    ) -> Optional[ModelRegistry]:
        """Update model details."""
        try:
            # Get existing model
            model = self.model_registry.get_model(model_id)
            if not model:
                return None
            
            # Update fields
            if model_name is not None:
                model.model_name = model_name
            if description is not None:
                model.description = description
            if parameters is not None:
                model.parameters = parameters
            if metrics is not None:
                model.metrics = metrics
            
            model.updated_at = datetime.utcnow()
            
            # Save changes
            session = self.model_registry.db_manager.get_session()
            try:
                session.commit()
                session.refresh(model)
                logger.info(f"Model {model_id} updated successfully")
                return model
            finally:
                self.model_registry.db_manager.close_session(session)
                
        except Exception as e:
            logger.error(f"Error updating model {model_id}: {str(e)}")
            raise
    
    def delete_model(self, model_id: str) -> bool:
        """Delete (deactivate) a model."""
        try:
            success = self.model_registry.delete_model(model_id)
            if success:
                logger.info(f"Model {model_id} deleted successfully")
            return success
            
        except Exception as e:
            logger.error(f"Error deleting model {model_id}: {str(e)}")
            raise
    
    def update_model_metrics(self, model_id: str, metrics: Dict[str, Any]) -> bool:
        """Update model performance metrics."""
        try:
            success = self.model_registry.update_model_metrics(model_id, metrics)
            if success:
                logger.info(f"Metrics updated for model {model_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error updating metrics for model {model_id}: {str(e)}")
            raise
    
    def get_model_types(self) -> List[str]:
        """Get list of available model types."""
        try:
            models = self.model_registry.list_models(active_only=True)
            types = list(set(model.model_type for model in models))
            return sorted(types)
            
        except Exception as e:
            logger.error(f"Error getting model types: {str(e)}")
            raise
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get model statistics."""
        try:
            models = self.model_registry.list_models(active_only=True)
            
            # Count by type
            type_counts = {}
            for model in models:
                type_counts[model.model_type] = type_counts.get(model.model_type, 0) + 1
            
            # Get recent models
            recent_models = sorted(
                models,
                key=lambda x: x.created_at,
                reverse=True
            )[:5]
            
            return {
                "total_models": len(models),
                "models_by_type": type_counts,
                "recent_models": [
                    {
                        "model_id": model.model_id,
                        "model_name": model.model_name,
                        "model_type": model.model_type,
                        "created_at": model.created_at
                    }
                    for model in recent_models
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting model stats: {str(e)}")
            raise
    
    def validate_model_path(self, model_path: str) -> bool:
        """Validate that a model path exists and is accessible."""
        try:
            if not os.path.exists(model_path):
                return False
            
            # Check if it's a directory (for local models)
            if os.path.isdir(model_path):
                # Check for common model files
                required_files = ["config.json", "pytorch_model.bin"]
                return all(os.path.exists(os.path.join(model_path, f)) for f in required_files)
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating model path {model_path}: {str(e)}")
            return False
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed model information."""
        try:
            model = self.model_registry.get_model(model_id)
            if not model:
                return None
            
            # Get model file size if path exists
            model_size = None
            if os.path.exists(model.model_path):
                if os.path.isdir(model.model_path):
                    model_size = sum(
                        os.path.getsize(os.path.join(dirpath, filename))
                        for dirpath, dirnames, filenames in os.walk(model.model_path)
                        for filename in filenames
                    )
                else:
                    model_size = os.path.getsize(model.model_path)
            
            return {
                "model_id": model.model_id,
                "model_name": model.model_name,
                "model_type": model.model_type,
                "model_path": model.model_path,
                "version": model.version,
                "description": model.description,
                "parameters": model.parameters,
                "metrics": model.metrics,
                "is_active": model.is_active,
                "created_at": model.created_at,
                "updated_at": model.updated_at,
                "model_size_bytes": model_size,
                "model_size_mb": round(model_size / (1024 * 1024), 2) if model_size else None
            }
            
        except Exception as e:
            logger.error(f"Error getting model info for {model_id}: {str(e)}")
            raise