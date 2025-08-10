"""
Inference Service

Business logic for model inference operations.
"""

from typing import List, Optional, Dict, Any, Union
import logging
import asyncio
from datetime import datetime

from ..core.database import InferenceLogManager
from ..core.config import get_settings
from llm.models.transformer_model import TransformerModel
from llm.models.text_classifier import TextClassifier
from llm.models.text_generator import TextGenerator

logger = logging.getLogger(__name__)

class InferenceService:
    """Service for model inference operations."""
    
    def __init__(self, inference_log: InferenceLogManager):
        """Initialize inference service."""
        self.inference_log = inference_log
        self.settings = get_settings()
        self._model_cache = {}
        self._default_models = {}
        
        # Initialize default models
        self._initialize_default_models()
    
    def _initialize_default_models(self):
        """Initialize default models for different tasks."""
        try:
            # Default text generation model
            self._default_models["text-generation"] = "gpt2"
            
            # Default classification model
            self._default_models["classification"] = "distilbert-base-uncased-finetuned-sst-2-english"
            
            # Default summarization model
            self._default_models["summarization"] = "facebook/bart-large-cnn"
            
            # Default QA model
            self._default_models["qa"] = "distilbert-base-cased-distilled-squad"
            
            logger.info("Default models initialized")
            
        except Exception as e:
            logger.error(f"Error initializing default models: {str(e)}")
    
    def _get_model(self, model_id: Optional[str], task_type: str) -> Union[TransformerModel, TextClassifier, TextGenerator]:
        """Get model instance from cache or load it."""
        try:
            # Use default model if no specific model_id provided
            if not model_id:
                model_id = self._default_models.get(task_type, "gpt2")
            
            # Check cache first
            if model_id in self._model_cache:
                return self._model_cache[model_id]
            
            # Load model based on task type
            if task_type == "text-generation":
                model = TextGenerator(model_id)
            elif task_type == "classification":
                model = TextClassifier(model_id)
            else:
                model = TransformerModel(model_id, task=task_type)
            
            # Cache the model
            self._model_cache[model_id] = model
            
            logger.info(f"Loaded model {model_id} for task {task_type}")
            return model
            
        except Exception as e:
            logger.error(f"Error loading model {model_id} for task {task_type}: {str(e)}")
            raise
    
    async def generate_text(
        self,
        prompt: str,
        model_id: Optional[str] = None,
        max_length: int = 100,
        min_length: int = 10,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        do_sample: bool = True,
        num_return_sequences: int = 1,
        repetition_penalty: float = 1.0
    ) -> Dict[str, Any]:
        """Generate text using a language model."""
        try:
            model = self._get_model(model_id, "text-generation")
            
            # Run generation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            generated_text = await loop.run_in_executor(
                None,
                lambda: model.generate(
                    prompt=prompt,
                    max_length=max_length,
                    min_length=min_length,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    do_sample=do_sample,
                    num_return_sequences=num_return_sequences,
                    repetition_penalty=repetition_penalty
                )
            )
            
            return {
                "generated_text": generated_text,
                "model_id": model_id or self._default_models["text-generation"],
                "prompt": prompt,
                "parameters": {
                    "max_length": max_length,
                    "min_length": min_length,
                    "temperature": temperature,
                    "top_p": top_p,
                    "top_k": top_k,
                    "do_sample": do_sample,
                    "num_return_sequences": num_return_sequences,
                    "repetition_penalty": repetition_penalty
                }
            }
            
        except Exception as e:
            logger.error(f"Error in text generation: {str(e)}")
            raise
    
    async def classify_text(
        self,
        text: str,
        model_id: Optional[str] = None,
        return_probabilities: bool = False,
        top_k: int = 3
    ) -> Dict[str, Any]:
        """Classify text using a classification model."""
        try:
            model = self._get_model(model_id, "classification")
            
            # Run classification in thread pool
            loop = asyncio.get_event_loop()
            
            if return_probabilities:
                result = await loop.run_in_executor(
                    None,
                    lambda: model.get_probabilities(text)
                )
            elif top_k > 1:
                result = await loop.run_in_executor(
                    None,
                    lambda: model.get_top_k_predictions(text, k=top_k)
                )
            else:
                result = await loop.run_in_executor(
                    None,
                    lambda: model.classify(text)
                )
            
            return {
                "classification": result,
                "model_id": model_id or self._default_models["classification"],
                "text": text,
                "return_probabilities": return_probabilities,
                "top_k": top_k
            }
            
        except Exception as e:
            logger.error(f"Error in text classification: {str(e)}")
            raise
    
    async def summarize_text(
        self,
        text: str,
        model_id: Optional[str] = None,
        max_length: int = 150,
        min_length: int = 30,
        do_sample: bool = False
    ) -> Dict[str, Any]:
        """Summarize text using a summarization model."""
        try:
            model = self._get_model(model_id, "summarization")
            
            # Run summarization in thread pool
            loop = asyncio.get_event_loop()
            summary = await loop.run_in_executor(
                None,
                lambda: model.summarize(text, max_length=max_length)
            )
            
            return {
                "summary": summary,
                "model_id": model_id or self._default_models["summarization"],
                "original_text": text,
                "parameters": {
                    "max_length": max_length,
                    "min_length": min_length,
                    "do_sample": do_sample
                }
            }
            
        except Exception as e:
            logger.error(f"Error in text summarization: {str(e)}")
            raise
    
    async def answer_question(
        self,
        question: str,
        context: str,
        model_id: Optional[str] = None,
        max_answer_length: int = 50
    ) -> Dict[str, Any]:
        """Answer questions using a QA model."""
        try:
            model = self._get_model(model_id, "qa")
            
            # Run QA in thread pool
            loop = asyncio.get_event_loop()
            answer = await loop.run_in_executor(
                None,
                lambda: model.answer_question(question, context)
            )
            
            return {
                "answer": answer,
                "model_id": model_id or self._default_models["qa"],
                "question": question,
                "context": context,
                "parameters": {
                    "max_answer_length": max_answer_length
                }
            }
            
        except Exception as e:
            logger.error(f"Error in question answering: {str(e)}")
            raise
    
    async def batch_inference(
        self,
        texts: List[str],
        task_type: str,
        model_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform batch inference on multiple texts."""
        try:
            model = self._get_model(model_id, task_type)
            parameters = parameters or {}
            
            # Run batch inference in thread pool
            loop = asyncio.get_event_loop()
            
            if task_type == "text-generation":
                results = []
                for text in texts:
                    result = await loop.run_in_executor(
                        None,
                        lambda t=text: model.generate(t, **parameters)
                    )
                    results.append(result)
                    
            elif task_type == "classification":
                results = await loop.run_in_executor(
                    None,
                    lambda: model.classify_batch(texts)
                )
                
            elif task_type == "summarization":
                results = []
                for text in texts:
                    result = await loop.run_in_executor(
                        None,
                        lambda t=text: model.summarize(t, **parameters)
                    )
                    results.append(result)
                    
            else:
                raise ValueError(f"Unsupported task type for batch inference: {task_type}")
            
            return {
                "results": results,
                "model_id": model_id or self._default_models.get(task_type, "default"),
                "task_type": task_type,
                "batch_size": len(texts),
                "parameters": parameters
            }
            
        except Exception as e:
            logger.error(f"Error in batch inference: {str(e)}")
            raise
    
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
    ):
        """Log inference request."""
        try:
            self.inference_log.log_inference(
                model_id=model_id,
                task_type=task_type,
                input_data=input_data,
                output_data=output_data,
                processing_time_ms=processing_time_ms,
                status=status,
                error_message=error_message,
                user_id=user_id,
                request_id=request_id
            )
            
        except Exception as e:
            logger.error(f"Error logging inference: {str(e)}")
    
    def get_inference_stats(
        self,
        model_id: Optional[str] = None,
        user_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get inference statistics."""
        try:
            return self.inference_log.get_inference_stats(
                model_id=model_id,
                user_id=user_id,
                days=days
            )
            
        except Exception as e:
            logger.error(f"Error getting inference stats: {str(e)}")
            raise
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models for inference."""
        try:
            models = []
            
            # Add default models
            for task_type, model_id in self._default_models.items():
                models.append({
                    "model_id": model_id,
                    "task_type": task_type,
                    "is_default": True,
                    "is_loaded": model_id in self._model_cache
                })
            
            # Add cached models
            for model_id, model in self._model_cache.items():
                if model_id not in self._default_models.values():
                    models.append({
                        "model_id": model_id,
                        "task_type": getattr(model, 'task', 'unknown'),
                        "is_default": False,
                        "is_loaded": True
                    })
            
            return models
            
        except Exception as e:
            logger.error(f"Error getting available models: {str(e)}")
            raise
    
    def clear_model_cache(self, model_id: Optional[str] = None):
        """Clear model cache."""
        try:
            if model_id:
                if model_id in self._model_cache:
                    del self._model_cache[model_id]
                    logger.info(f"Cleared model {model_id} from cache")
            else:
                self._model_cache.clear()
                logger.info("Cleared all models from cache")
                
        except Exception as e:
            logger.error(f"Error clearing model cache: {str(e)}")
            raise
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model."""
        try:
            if model_id in self._model_cache:
                model = self._model_cache[model_id]
                return model.get_model_info()
            else:
                # Try to load model info without caching
                try:
                    model = self._get_model(model_id, "text-generation")
                    info = model.get_model_info()
                    # Remove from cache since we just wanted info
                    if model_id in self._model_cache:
                        del self._model_cache[model_id]
                    return info
                except:
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting model info for {model_id}: {str(e)}")
            return None