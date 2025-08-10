"""
Configuration utilities for the LLM package.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
import json

@dataclass
class Config:
    """Configuration class for LLM models."""
    
    # Model configuration
    model_name: str
    task_type: str = "text-generation"
    device: str = "auto"
    cache_dir: Optional[str] = None
    
    # Generation parameters
    max_length: int = 100
    min_length: int = 10
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    do_sample: bool = True
    num_return_sequences: int = 1
    repetition_penalty: float = 1.0
    
    # Training parameters
    learning_rate: float = 5e-5
    batch_size: int = 8
    num_epochs: int = 3
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """Create Config from dictionary."""
        return cls(**config_dict)
    
    @classmethod
    def from_file(cls, file_path: str) -> 'Config':
        """Load Config from JSON file."""
        with open(file_path, 'r') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Config to dictionary."""
        return {
            'model_name': self.model_name,
            'task_type': self.task_type,
            'device': self.device,
            'cache_dir': self.cache_dir,
            'max_length': self.max_length,
            'min_length': self.min_length,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'top_k': self.top_k,
            'do_sample': self.do_sample,
            'num_return_sequences': self.num_return_sequences,
            'repetition_penalty': self.repetition_penalty,
            'learning_rate': self.learning_rate,
            'batch_size': self.batch_size,
            'num_epochs': self.num_epochs
        }
    
    def save(self, file_path: str):
        """Save Config to JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def get_device(self) -> str:
        """Get the appropriate device for the model."""
        if self.device == "auto":
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        return self.device