"""
LLM (Language Learning Model) Package

A comprehensive package for natural language processing and machine learning
using transformer-based models.
"""

__version__ = "1.0.0"
__author__ = "LLM Development Team"

from .models.transformer_model import TransformerModel
from .models.text_classifier import TextClassifier
from .models.text_generator import TextGenerator

__all__ = [
    "TransformerModel",
    "TextClassifier", 
    "TextGenerator"
]