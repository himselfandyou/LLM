#!/usr/bin/env python3
"""
Simple working server that demonstrates LLM functionality via API.
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import time

# Import our LLM components
from llm.models.text_generator import TextGenerator
from llm.models.text_classifier import TextClassifier

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Simple LLM Server",
    description="A simple server demonstrating LLM functionality",
    version="1.0.0"
)

# Global model instances
generator = None
classifier = None

# Pydantic models
class GenerateRequest(BaseModel):
    prompt: str
    max_length: Optional[int] = 100
    temperature: Optional[float] = 0.7

class ClassifyRequest(BaseModel):
    text: str

class GenerateResponse(BaseModel):
    generated_text: str
    processing_time_ms: int
    model_used: str

class ClassifyResponse(BaseModel):
    classification: Dict[str, Any]
    processing_time_ms: int
    model_used: str

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup."""
    global generator, classifier
    
    logger.info("Initializing models...")
    
    try:
        # Initialize text generator
        generator = TextGenerator("gpt2")
        logger.info("Text generator initialized successfully")
        
        # Initialize text classifier
        classifier = TextClassifier("distilbert-base-uncased-finetuned-sst-2-english")
        logger.info("Text classifier initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing models: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Simple LLM Server is running",
        "version": "1.0.0",
        "endpoints": {
            "generate": "/generate",
            "classify": "/classify",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "models_loaded": {
            "generator": generator is not None,
            "classifier": classifier is not None
        }
    }

@app.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    """Generate text using the language model."""
    if generator is None:
        raise HTTPException(status_code=500, detail="Text generator not initialized")
    
    try:
        start_time = time.time()
        
        # Generate text
        generated_text = generator.generate(
            prompt=request.prompt,
            max_length=request.max_length,
            temperature=request.temperature
        )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return GenerateResponse(
            generated_text=generated_text,
            processing_time_ms=processing_time_ms,
            model_used="gpt2"
        )
        
    except Exception as e:
        logger.error(f"Error in text generation: {e}")
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")

@app.post("/classify", response_model=ClassifyResponse)
async def classify_text(request: ClassifyRequest):
    """Classify text using the classification model."""
    if classifier is None:
        raise HTTPException(status_code=500, detail="Text classifier not initialized")
    
    try:
        start_time = time.time()
        
        # Classify text
        classification = classifier.classify(request.text)
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return ClassifyResponse(
            classification=classification,
            processing_time_ms=processing_time_ms,
            model_used="distilbert-base-uncased-finetuned-sst-2-english"
        )
        
    except Exception as e:
        logger.error(f"Error in text classification: {e}")
        raise HTTPException(status_code=500, detail=f"Text classification failed: {str(e)}")

@app.get("/models")
async def get_models():
    """Get information about loaded models."""
    return {
        "generator": {
            "model_name": "gpt2",
            "loaded": generator is not None,
            "type": "text-generation"
        },
        "classifier": {
            "model_name": "distilbert-base-uncased-finetuned-sst-2-english",
            "loaded": classifier is not None,
            "type": "text-classification"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )