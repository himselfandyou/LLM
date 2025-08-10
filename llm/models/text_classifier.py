"""
Text Classifier Model

A specialized model for text classification tasks including sentiment analysis,
topic classification, and intent detection.
"""

import torch
import torch.nn as nn
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline
)
from typing import Dict, List, Optional, Any, Union
import logging
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import json
import os

logger = logging.getLogger(__name__)

class TextClassifier:
    """
    A specialized text classifier for various classification tasks.
    
    Supports:
    - Sentiment analysis (positive, negative, neutral)
    - Topic classification
    - Intent detection
    - Custom multi-label classification
    """
    
    def __init__(
        self,
        model_name: str,
        labels: Optional[List[str]] = None,
        device: Optional[str] = None,
        cache_dir: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the text classifier.
        
        Args:
            model_name: Name or path of the pre-trained model
            labels: List of class labels
            device: Device to run the model on
            cache_dir: Directory to cache model files
            **kwargs: Additional arguments for model initialization
        """
        self.model_name = model_name
        self.labels = labels
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.cache_dir = cache_dir
        
        logger.info(f"Initializing text classifier: {model_name} on {self.device}")
        
        # Initialize tokenizer and model
        self._initialize_model(**kwargs)
        
    def _initialize_model(self, **kwargs):
        """Initialize the model and tokenizer."""
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
            
            # Load model
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir,
                **kwargs
            )
            
            # Move model to device
            self.model.to(self.device)
            self.model.eval()
            
            # Create pipeline
            self.pipeline = pipeline(
                "text-classification",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1
            )
            
            # Get labels from model config if not provided
            if self.labels is None:
                self.labels = list(self.model.config.id2label.values())
            
            logger.info(f"Text classifier {self.model_name} loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading text classifier {self.model_name}: {str(e)}")
            raise
    
    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classify the given text.
        
        Args:
            text: Input text to classify
            
        Returns:
            Classification result with label and confidence score
        """
        result = self.pipeline(text)
        return result[0]
    
    def classify_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Classify a batch of texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of classification results
        """
        results = self.pipeline(texts)
        return results
    
    def get_probabilities(self, text: str) -> Dict[str, float]:
        """
        Get probability scores for all classes.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary mapping class labels to probabilities
        """
        # Tokenize input
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.device)
        
        # Get model outputs
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)
        
        # Convert to dictionary
        prob_dict = {}
        for i, label in enumerate(self.labels):
            prob_dict[label] = probabilities[0][i].item()
        
        return prob_dict
    
    def get_top_k_predictions(self, text: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Get top-k predictions for the given text.
        
        Args:
            text: Input text
            k: Number of top predictions to return
            
        Returns:
            List of top-k predictions with labels and scores
        """
        probabilities = self.get_probabilities(text)
        
        # Sort by probability
        sorted_probs = sorted(
            probabilities.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return top-k
        top_k = []
        for label, prob in sorted_probs[:k]:
            top_k.append({
                "label": label,
                "score": prob
            })
        
        return top_k
    
    def evaluate(self, texts: List[str], true_labels: List[str]) -> Dict[str, Any]:
        """
        Evaluate the classifier on a test set.
        
        Args:
            texts: List of test texts
            true_labels: List of true labels
            
        Returns:
            Evaluation metrics
        """
        if len(texts) != len(true_labels):
            raise ValueError("Number of texts and labels must be equal")
        
        # Get predictions
        predictions = self.classify_batch(texts)
        pred_labels = [pred["label"] for pred in predictions]
        
        # Calculate metrics
        report = classification_report(
            true_labels,
            pred_labels,
            labels=self.labels,
            output_dict=True
        )
        
        # Calculate confusion matrix
        cm = confusion_matrix(true_labels, pred_labels, labels=self.labels)
        
        # Calculate accuracy
        accuracy = sum(1 for p, t in zip(pred_labels, true_labels) if p == t) / len(true_labels)
        
        return {
            "accuracy": accuracy,
            "classification_report": report,
            "confusion_matrix": cm.tolist(),
            "predictions": pred_labels,
            "true_labels": true_labels
        }
    
    def fine_tune(
        self,
        train_texts: List[str],
        train_labels: List[str],
        val_texts: Optional[List[str]] = None,
        val_labels: Optional[List[str]] = None,
        output_dir: str = "./fine_tuned_classifier",
        num_epochs: int = 3,
        batch_size: int = 16,
        learning_rate: float = 2e-5,
        **kwargs
    ):
        """
        Fine-tune the classifier on custom data.
        
        Args:
            train_texts: Training texts
            train_labels: Training labels
            val_texts: Validation texts
            val_labels: Validation labels
            output_dir: Directory to save the fine-tuned model
            num_epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate for training
            **kwargs: Additional training arguments
        """
        from transformers import Trainer, TrainingArguments
        from datasets import Dataset
        
        # Create datasets
        train_dataset = Dataset.from_dict({
            "text": train_texts,
            "label": train_labels
        })
        
        if val_texts and val_labels:
            val_dataset = Dataset.from_dict({
                "text": val_texts,
                "label": val_labels
            })
        else:
            val_dataset = None
        
        # Tokenize datasets
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                padding="max_length",
                truncation=True,
                max_length=512
            )
        
        train_dataset = train_dataset.map(tokenize_function, batched=True)
        if val_dataset:
            val_dataset = val_dataset.map(tokenize_function, batched=True)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            save_steps=500,
            save_total_limit=2,
            evaluation_strategy="epoch" if val_dataset else "no",
            **kwargs
        )
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=self.tokenizer
        )
        
        # Train
        trainer.train()
        
        # Save model
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        # Save labels
        with open(os.path.join(output_dir, "labels.json"), "w") as f:
            json.dump(self.labels, f)
        
        logger.info(f"Classifier fine-tuned and saved to {output_dir}")
    
    def save(self, path: str):
        """Save the classifier to the specified path."""
        os.makedirs(path, exist_ok=True)
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
        
        # Save labels
        with open(os.path.join(path, "labels.json"), "w") as f:
            json.dump(self.labels, f)
        
        # Save metadata
        metadata = {
            "model_name": self.model_name,
            "labels": self.labels,
            "device": self.device
        }
        
        with open(os.path.join(path, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Classifier saved to {path}")
    
    @classmethod
    def load(cls, path: str, device: Optional[str] = None):
        """Load a saved classifier from the specified path."""
        # Load labels
        labels_path = os.path.join(path, "labels.json")
        labels = None
        if os.path.exists(labels_path):
            with open(labels_path, "r") as f:
                labels = json.load(f)
        
        # Load metadata
        metadata_path = os.path.join(path, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            
            return cls(
                model_name=path,
                labels=labels,
                device=device or metadata.get("device", "cpu")
            )
        else:
            return cls(model_name=path, labels=labels, device=device)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the classifier."""
        return {
            "model_name": self.model_name,
            "labels": self.labels,
            "num_classes": len(self.labels),
            "device": self.device,
            "num_parameters": sum(p.numel() for p in self.model.parameters())
        }