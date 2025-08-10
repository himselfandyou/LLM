"""
Inference API Routes

API endpoints for model inference and predictions.
"""

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import logging
import time
import uuid
from datetime import datetime

from ...core.database import InferenceLogManager, DatabaseManager
from ...core.config import get_settings
from ...services.inference_service import InferenceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/inference", tags=["inference"])

# Pydantic models for request/response
class TextGenerationRequest(BaseModel):
    prompt: str
    max_length: Optional[int] = 100
    min_length: Optional[int] = 10
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    top_k: Optional[int] = 50
    do_sample: Optional[bool] = True
    num_return_sequences: Optional[int] = 1
    repetition_penalty: Optional[float] = 1.0

class TextClassificationRequest(BaseModel):
    text: str
    return_probabilities: Optional[bool] = False
    top_k: Optional[int] = 3

class TextSummarizationRequest(BaseModel):
    text: str
    max_length: Optional[int] = 150
    min_length: Optional[int] = 30
    do_sample: Optional[bool] = False

class QuestionAnsweringRequest(BaseModel):
    question: str
    context: str
    max_answer_length: Optional[int] = 50

class BatchInferenceRequest(BaseModel):
    texts: List[str]
    task_type: str  # generate, classify, summarize
    parameters: Optional[Dict[str, Any]] = None

class InferenceResponse(BaseModel):
    request_id: str
    model_id: str
    task_type: str
    result: Union[str, Dict[str, Any], List[Dict[str, Any]]]
    processing_time_ms: int
    timestamp: datetime

class BatchInferenceResponse(BaseModel):
    request_id: str
    model_id: str
    task_type: str
    results: List[Union[str, Dict[str, Any]]]
    processing_time_ms: int
    timestamp: datetime

# Dependency injection
def get_inference_service():
    """Get inference service instance."""
    settings = get_settings()
    db_manager = DatabaseManager(settings.database_url or "sqlite:///./mcp_server.db")
    inference_log = InferenceLogManager(db_manager)
    return InferenceService(inference_log)

@router.post("/generate", response_model=InferenceResponse)
async def generate_text(
    request: TextGenerationRequest,
    model_id: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    inference_service: InferenceService = Depends(get_inference_service)
):
    """
    Generate text using a language model.
    
    Args:
        request: Text generation request
        model_id: Model identifier (uses default if not specified)
        background_tasks: Background tasks for logging
        inference_service: Inference service instance
        
    Returns:
        Generated text with metadata
    """
    try:
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Generate text
        result = await inference_service.generate_text(
            prompt=request.prompt,
            model_id=model_id,
            max_length=request.max_length,
            min_length=request.min_length,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
            do_sample=request.do_sample,
            num_return_sequences=request.num_return_sequences,
            repetition_penalty=request.repetition_penalty
        )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Log inference in background
        if background_tasks:
            background_tasks.add_task(
                inference_service.log_inference,
                model_id=result.get("model_id", model_id or "default"),
                task_type="generate",
                input_data=request.prompt,
                output_data=str(result.get("generated_text", "")),
                processing_time_ms=processing_time_ms,
                request_id=request_id
            )
        
        return InferenceResponse(
            request_id=request_id,
            model_id=result.get("model_id", model_id or "default"),
            task_type="generate",
            result=result.get("generated_text", ""),
            processing_time_ms=processing_time_ms,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error in text generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text generation failed: {str(e)}"
        )

@router.post("/classify", response_model=InferenceResponse)
async def classify_text(
    request: TextClassificationRequest,
    model_id: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    inference_service: InferenceService = Depends(get_inference_service)
):
    """
    Classify text using a classification model.
    
    Args:
        request: Text classification request
        model_id: Model identifier (uses default if not specified)
        background_tasks: Background tasks for logging
        inference_service: Inference service instance
        
    Returns:
        Classification results with metadata
    """
    try:
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Classify text
        result = await inference_service.classify_text(
            text=request.text,
            model_id=model_id,
            return_probabilities=request.return_probabilities,
            top_k=request.top_k
        )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Log inference in background
        if background_tasks:
            background_tasks.add_task(
                inference_service.log_inference,
                model_id=result.get("model_id", model_id or "default"),
                task_type="classify",
                input_data=request.text,
                output_data=str(result.get("classification", "")),
                processing_time_ms=processing_time_ms,
                request_id=request_id
            )
        
        return InferenceResponse(
            request_id=request_id,
            model_id=result.get("model_id", model_id or "default"),
            task_type="classify",
            result=result.get("classification", {}),
            processing_time_ms=processing_time_ms,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error in text classification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text classification failed: {str(e)}"
        )

@router.post("/summarize", response_model=InferenceResponse)
async def summarize_text(
    request: TextSummarizationRequest,
    model_id: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    inference_service: InferenceService = Depends(get_inference_service)
):
    """
    Summarize text using a summarization model.
    
    Args:
        request: Text summarization request
        model_id: Model identifier (uses default if not specified)
        background_tasks: Background tasks for logging
        inference_service: Inference service instance
        
    Returns:
        Generated summary with metadata
    """
    try:
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Summarize text
        result = await inference_service.summarize_text(
            text=request.text,
            model_id=model_id,
            max_length=request.max_length,
            min_length=request.min_length,
            do_sample=request.do_sample
        )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Log inference in background
        if background_tasks:
            background_tasks.add_task(
                inference_service.log_inference,
                model_id=result.get("model_id", model_id or "default"),
                task_type="summarize",
                input_data=request.text,
                output_data=result.get("summary", ""),
                processing_time_ms=processing_time_ms,
                request_id=request_id
            )
        
        return InferenceResponse(
            request_id=request_id,
            model_id=result.get("model_id", model_id or "default"),
            task_type="summarize",
            result=result.get("summary", ""),
            processing_time_ms=processing_time_ms,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error in text summarization: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text summarization failed: {str(e)}"
        )

@router.post("/qa", response_model=InferenceResponse)
async def answer_question(
    request: QuestionAnsweringRequest,
    model_id: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    inference_service: InferenceService = Depends(get_inference_service)
):
    """
    Answer questions using a question-answering model.
    
    Args:
        request: Question answering request
        model_id: Model identifier (uses default if not specified)
        background_tasks: Background tasks for logging
        inference_service: Inference service instance
        
    Returns:
        Answer with metadata
    """
    try:
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Answer question
        result = await inference_service.answer_question(
            question=request.question,
            context=request.context,
            model_id=model_id,
            max_answer_length=request.max_answer_length
        )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Log inference in background
        if background_tasks:
            background_tasks.add_task(
                inference_service.log_inference,
                model_id=result.get("model_id", model_id or "default"),
                task_type="qa",
                input_data=f"Q: {request.question}\nC: {request.context}",
                output_data=str(result.get("answer", "")),
                processing_time_ms=processing_time_ms,
                request_id=request_id
            )
        
        return InferenceResponse(
            request_id=request_id,
            model_id=result.get("model_id", model_id or "default"),
            task_type="qa",
            result=result.get("answer", {}),
            processing_time_ms=processing_time_ms,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error in question answering: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Question answering failed: {str(e)}"
        )

@router.post("/batch", response_model=BatchInferenceResponse)
async def batch_inference(
    request: BatchInferenceRequest,
    model_id: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    inference_service: InferenceService = Depends(get_inference_service)
):
    """
    Perform batch inference on multiple texts.
    
    Args:
        request: Batch inference request
        model_id: Model identifier (uses default if not specified)
        background_tasks: Background tasks for logging
        inference_service: Inference service instance
        
    Returns:
        Batch results with metadata
    """
    try:
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Perform batch inference
        result = await inference_service.batch_inference(
            texts=request.texts,
            task_type=request.task_type,
            model_id=model_id,
            parameters=request.parameters
        )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Log inference in background
        if background_tasks:
            background_tasks.add_task(
                inference_service.log_inference,
                model_id=result.get("model_id", model_id or "default"),
                task_type=f"batch_{request.task_type}",
                input_data=str(request.texts),
                output_data=str(result.get("results", [])),
                processing_time_ms=processing_time_ms,
                request_id=request_id
            )
        
        return BatchInferenceResponse(
            request_id=request_id,
            model_id=result.get("model_id", model_id or "default"),
            task_type=request.task_type,
            results=result.get("results", []),
            processing_time_ms=processing_time_ms,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error in batch inference: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch inference failed: {str(e)}"
        )

@router.get("/stats")
async def get_inference_stats(
    model_id: Optional[str] = None,
    days: int = 30,
    inference_service: InferenceService = Depends(get_inference_service)
):
    """
    Get inference statistics.
    
    Args:
        model_id: Model identifier (optional)
        days: Number of days to look back
        inference_service: Inference service instance
        
    Returns:
        Inference statistics
    """
    try:
        stats = inference_service.get_inference_stats(
            model_id=model_id,
            days=days
        )
        
        return {
            "model_id": model_id,
            "period_days": days,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting inference stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get inference statistics"
        )

@router.get("/models")
async def get_available_models(
    inference_service: InferenceService = Depends(get_inference_service)
):
    """
    Get list of available models for inference.
    
    Args:
        inference_service: Inference service instance
        
    Returns:
        List of available models
    """
    try:
        models = inference_service.get_available_models()
        
        return {
            "models": models,
            "total": len(models)
        }
        
    except Exception as e:
        logger.error(f"Error getting available models: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available models"
        )