"""
Database Management

Database connection and management for the MCP Server.
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

Base = declarative_base()

class ModelRegistry(Base):
    """Model registry table for storing model metadata."""
    
    __tablename__ = "model_registry"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String(255), unique=True, index=True, nullable=False)
    model_name = Column(String(255), nullable=False)
    model_type = Column(String(100), nullable=False)  # text-generation, classification, etc.
    model_path = Column(String(500), nullable=False)
    version = Column(String(50), default="1.0.0")
    description = Column(Text)
    parameters = Column(JSON)  # Model parameters and configuration
    metrics = Column(JSON)  # Model performance metrics
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class InferenceLog(Base):
    """Inference log table for tracking model usage."""
    
    __tablename__ = "inference_log"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String(255), index=True, nullable=False)
    request_id = Column(String(255), index=True)
    task_type = Column(String(100), nullable=False)  # generate, classify, etc.
    input_data = Column(Text)
    output_data = Column(Text)
    processing_time_ms = Column(Integer)
    status = Column(String(50), default="success")  # success, error, timeout
    error_message = Column(Text)
    user_id = Column(String(255), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    """User table for authentication and authorization."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    api_key = Column(String(255), unique=True, index=True)
    rate_limit = Column(Integer, default=100)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DatabaseManager:
    """Database manager for handling database operations."""
    
    def __init__(self, database_url: str):
        """Initialize database manager."""
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection and create tables."""
        try:
            self.engine = create_engine(
                self.database_url,
                pool_pre_ping=True,
                pool_recycle=300
            )
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def get_session(self) -> Session:
        """Get database session."""
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()
    
    def close_session(self, session: Session):
        """Close database session."""
        session.close()

class ModelRegistryManager:
    """Manager for model registry operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize model registry manager."""
        self.db_manager = db_manager
    
    def register_model(
        self,
        model_id: str,
        model_name: str,
        model_type: str,
        model_path: str,
        version: str = "1.0.0",
        description: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None
    ) -> ModelRegistry:
        """Register a new model in the registry."""
        session = self.db_manager.get_session()
        try:
            # Check if model already exists
            existing_model = session.query(ModelRegistry).filter(
                ModelRegistry.model_id == model_id
            ).first()
            
            if existing_model:
                # Update existing model
                existing_model.model_name = model_name
                existing_model.model_type = model_type
                existing_model.model_path = model_path
                existing_model.version = version
                existing_model.description = description
                existing_model.parameters = parameters
                existing_model.metrics = metrics
                existing_model.updated_at = datetime.utcnow()
                
                session.commit()
                logger.info(f"Updated model {model_id} in registry")
                return existing_model
            else:
                # Create new model
                model = ModelRegistry(
                    model_id=model_id,
                    model_name=model_name,
                    model_type=model_type,
                    model_path=model_path,
                    version=version,
                    description=description,
                    parameters=parameters,
                    metrics=metrics
                )
                
                session.add(model)
                session.commit()
                session.refresh(model)
                
                logger.info(f"Registered model {model_id} in registry")
                return model
                
        except Exception as e:
            session.rollback()
            logger.error(f"Error registering model {model_id}: {str(e)}")
            raise
        finally:
            self.db_manager.close_session(session)
    
    def get_model(self, model_id: str) -> Optional[ModelRegistry]:
        """Get model from registry by ID."""
        session = self.db_manager.get_session()
        try:
            model = session.query(ModelRegistry).filter(
                ModelRegistry.model_id == model_id,
                ModelRegistry.is_active == True
            ).first()
            return model
        finally:
            self.db_manager.close_session(session)
    
    def list_models(
        self,
        model_type: Optional[str] = None,
        active_only: bool = True
    ) -> List[ModelRegistry]:
        """List models in registry."""
        session = self.db_manager.get_session()
        try:
            query = session.query(ModelRegistry)
            
            if model_type:
                query = query.filter(ModelRegistry.model_type == model_type)
            
            if active_only:
                query = query.filter(ModelRegistry.is_active == True)
            
            return query.all()
        finally:
            self.db_manager.close_session(session)
    
    def delete_model(self, model_id: str) -> bool:
        """Delete model from registry."""
        session = self.db_manager.get_session()
        try:
            model = session.query(ModelRegistry).filter(
                ModelRegistry.model_id == model_id
            ).first()
            
            if model:
                model.is_active = False
                session.commit()
                logger.info(f"Deactivated model {model_id} in registry")
                return True
            else:
                logger.warning(f"Model {model_id} not found in registry")
                return False
                
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting model {model_id}: {str(e)}")
            raise
        finally:
            self.db_manager.close_session(session)
    
    def update_model_metrics(
        self,
        model_id: str,
        metrics: Dict[str, Any]
    ) -> bool:
        """Update model metrics."""
        session = self.db_manager.get_session()
        try:
            model = session.query(ModelRegistry).filter(
                ModelRegistry.model_id == model_id
            ).first()
            
            if model:
                model.metrics = metrics
                model.updated_at = datetime.utcnow()
                session.commit()
                logger.info(f"Updated metrics for model {model_id}")
                return True
            else:
                logger.warning(f"Model {model_id} not found in registry")
                return False
                
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating metrics for model {model_id}: {str(e)}")
            raise
        finally:
            self.db_manager.close_session(session)

class InferenceLogManager:
    """Manager for inference logging operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize inference log manager."""
        self.db_manager = db_manager
    
    def log_inference(
        self,
        model_id: str,
        task_type: str,
        input_data: str,
        output_data: str,
        processing_time_ms: int,
        status: str = "success",
        error_message: Optional[str] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> InferenceLog:
        """Log an inference request."""
        session = self.db_manager.get_session()
        try:
            log_entry = InferenceLog(
                model_id=model_id,
                request_id=request_id,
                task_type=task_type,
                input_data=input_data,
                output_data=output_data,
                processing_time_ms=processing_time_ms,
                status=status,
                error_message=error_message,
                user_id=user_id
            )
            
            session.add(log_entry)
            session.commit()
            session.refresh(log_entry)
            
            return log_entry
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error logging inference: {str(e)}")
            raise
        finally:
            self.db_manager.close_session(session)
    
    def get_inference_stats(
        self,
        model_id: Optional[str] = None,
        user_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get inference statistics."""
        session = self.db_manager.get_session()
        try:
            from datetime import timedelta
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            query = session.query(InferenceLog).filter(
                InferenceLog.created_at >= start_date,
                InferenceLog.created_at <= end_date
            )
            
            if model_id:
                query = query.filter(InferenceLog.model_id == model_id)
            
            if user_id:
                query = query.filter(InferenceLog.user_id == user_id)
            
            logs = query.all()
            
            # Calculate statistics
            total_requests = len(logs)
            successful_requests = len([log for log in logs if log.status == "success"])
            failed_requests = total_requests - successful_requests
            
            avg_processing_time = 0
            if successful_requests > 0:
                avg_processing_time = sum(
                    log.processing_time_ms for log in logs if log.status == "success"
                ) / successful_requests
            
            return {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
                "avg_processing_time_ms": avg_processing_time,
                "period_days": days
            }
            
        finally:
            self.db_manager.close_session(session)