"""
Transformer Model Implementation

A comprehensive transformer-based model for various NLP tasks including
text generation, classification, and fine-tuning.
"""

import torch
import torch.nn as nn
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    AutoModelForQuestionAnswering,
    AutoModelForSeq2SeqLM,
    pipeline,
    GenerationConfig
)
from typing import Dict, List, Optional, Union, Any
import logging
import json
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class GenerationParams:
    """Parameters for text generation."""
    max_length: int = 100
    min_length: int = 10
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    do_sample: bool = True
    num_return_sequences: int = 1
    pad_token_id: Optional[int] = None
    eos_token_id: Optional[int] = None
    repetition_penalty: float = 1.0

class TransformerModel:
    """
    A flexible transformer-based model wrapper for various NLP tasks.
    
    Supports:
    - Text generation (causal language modeling)
    - Text classification
    - Named Entity Recognition
    - Question Answering
    - Text summarization
    """
    
    def __init__(
        self,
        model_name: str,
        task: str = "text-generation",
        device: Optional[str] = None,
        cache_dir: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the transformer model.
        
        Args:
            model_name: Name or path of the pre-trained model
            task: NLP task type ('text-generation', 'classification', 'ner', 'qa', 'summarization')
            device: Device to run the model on ('cpu', 'cuda', 'mps')
            cache_dir: Directory to cache model files
            **kwargs: Additional arguments for model initialization
        """
        self.model_name = model_name
        self.task = task
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.cache_dir = cache_dir
        
        logger.info(f"Initializing {task} model: {model_name} on {self.device}")
        
        # Initialize tokenizer and model based on task
        self._initialize_model(**kwargs)
        
    def _initialize_model(self, **kwargs):
        """Initialize the model and tokenizer based on the task."""
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir,
                **kwargs
            )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model based on task
            if self.task == "text-generation":
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    cache_dir=self.cache_dir,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    **kwargs
                )
            elif self.task == "classification":
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_name,
                    cache_dir=self.cache_dir,
                    **kwargs
                )
            elif self.task == "ner":
                self.model = AutoModelForTokenClassification.from_pretrained(
                    self.model_name,
                    cache_dir=self.cache_dir,
                    **kwargs
                )
            elif self.task == "qa":
                self.model = AutoModelForQuestionAnswering.from_pretrained(
                    self.model_name,
                    cache_dir=self.cache_dir,
                    **kwargs
                )
            elif self.task == "summarization":
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    self.model_name,
                    cache_dir=self.cache_dir,
                    **kwargs
                )
            else:
                raise ValueError(f"Unsupported task: {self.task}")
            
            # Move model to device
            self.model.to(self.device)
            self.model.eval()
            
            # Create pipeline for easy inference
            self.pipeline = pipeline(
                self.task,
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1
            )
            
            logger.info(f"Model {self.model_name} loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {str(e)}")
            raise
    
    def generate(
        self,
        prompt: str,
        params: Optional[GenerationParams] = None,
        **kwargs
    ) -> str:
        """
        Generate text based on the given prompt.
        
        Args:
            prompt: Input text prompt
            params: Generation parameters
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        if self.task != "text-generation":
            raise ValueError(f"Model is not configured for text generation (task: {self.task})")
        
        params = params or GenerationParams()
        
        # Prepare generation config
        generation_config = GenerationConfig(
            max_length=params.max_length,
            min_length=params.min_length,
            temperature=params.temperature,
            top_p=params.top_p,
            top_k=params.top_k,
            do_sample=params.do_sample,
            num_return_sequences=params.num_return_sequences,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
            repetition_penalty=params.repetition_penalty,
            **kwargs
        )
        
        # Tokenize input
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            truncation=True
        ).to(self.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                generation_config=generation_config
            )
        
        # Decode output
        generated_text = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )
        
        return generated_text
    
    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classify the given text.
        
        Args:
            text: Input text to classify
            
        Returns:
            Classification results
        """
        if self.task != "classification":
            raise ValueError(f"Model is not configured for classification (task: {self.task})")
        
        result = self.pipeline(text)
        return result
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from the given text.
        
        Args:
            text: Input text
            
        Returns:
            List of extracted entities
        """
        if self.task != "ner":
            raise ValueError(f"Model is not configured for NER (task: {self.task})")
        
        result = self.pipeline(text)
        return result
    
    def answer_question(self, question: str, context: str) -> Dict[str, Any]:
        """
        Answer a question based on the given context.
        
        Args:
            question: The question to answer
            context: The context to search for the answer
            
        Returns:
            Answer and confidence score
        """
        if self.task != "qa":
            raise ValueError(f"Model is not configured for QA (task: {self.task})")
        
        result = self.pipeline(question=question, context=context)
        return result
    
    def summarize(self, text: str, max_length: int = 150) -> str:
        """
        Summarize the given text.
        
        Args:
            text: Input text to summarize
            max_length: Maximum length of the summary
            
        Returns:
            Generated summary
        """
        if self.task != "summarization":
            raise ValueError(f"Model is not configured for summarization (task: {self.task})")
        
        result = self.pipeline(text, max_length=max_length, min_length=30)
        return result[0]['summary_text']
    
    def fine_tune(
        self,
        train_dataset,
        eval_dataset=None,
        output_dir: str = "./fine_tuned_model",
        num_epochs: int = 3,
        batch_size: int = 8,
        learning_rate: float = 5e-5,
        **kwargs
    ):
        """
        Fine-tune the model on custom data.
        
        Args:
            train_dataset: Training dataset
            eval_dataset: Evaluation dataset
            output_dir: Directory to save the fine-tuned model
            num_epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate for training
            **kwargs: Additional training arguments
        """
        from transformers import Trainer, TrainingArguments
        
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            save_steps=1000,
            save_total_limit=2,
            **kwargs
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=self.tokenizer
        )
        
        trainer.train()
        
        # Save the fine-tuned model
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        logger.info(f"Model fine-tuned and saved to {output_dir}")
    
    def save(self, path: str):
        """Save the model and tokenizer to the specified path."""
        os.makedirs(path, exist_ok=True)
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
        
        # Save model metadata
        metadata = {
            "model_name": self.model_name,
            "task": self.task,
            "device": self.device
        }
        
        with open(os.path.join(path, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Model saved to {path}")
    
    @classmethod
    def load(cls, path: str, device: Optional[str] = None):
        """Load a saved model from the specified path."""
        metadata_path = os.path.join(path, "metadata.json")
        
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            
            return cls(
                model_name=path,
                task=metadata.get("task", "text-generation"),
                device=device or metadata.get("device", "cpu")
            )
        else:
            return cls(model_name=path, device=device)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model."""
        return {
            "model_name": self.model_name,
            "task": self.task,
            "device": self.device,
            "num_parameters": sum(p.numel() for p in self.model.parameters()),
            "trainable_parameters": sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        }