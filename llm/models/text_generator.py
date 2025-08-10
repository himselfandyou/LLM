"""
Text Generator Model

A specialized model for text generation tasks including story generation,
poetry generation, and creative writing.
"""

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    pipeline,
    GenerationConfig
)
from typing import Dict, List, Optional, Any, Union
import logging
import json
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class GenerationConfig:
    """Configuration for text generation."""
    max_length: int = 100
    min_length: int = 10
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    do_sample: bool = True
    num_return_sequences: int = 1
    repetition_penalty: float = 1.0
    length_penalty: float = 1.0
    no_repeat_ngram_size: int = 3
    early_stopping: bool = True
    pad_token_id: Optional[int] = None
    eos_token_id: Optional[int] = None

class TextGenerator:
    """
    A specialized text generator for various creative writing tasks.
    
    Supports:
    - Story generation
    - Poetry generation
    - Creative writing
    - Text completion
    - Dialogue generation
    """
    
    def __init__(
        self,
        model_name: str,
        device: Optional[str] = None,
        cache_dir: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the text generator.
        
        Args:
            model_name: Name or path of the pre-trained model
            device: Device to run the model on
            cache_dir: Directory to cache model files
            **kwargs: Additional arguments for model initialization
        """
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.cache_dir = cache_dir
        
        logger.info(f"Initializing text generator: {model_name} on {self.device}")
        
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
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                **kwargs
            )
            
            # Move model to device
            self.model.to(self.device)
            self.model.eval()
            
            # Create pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1
            )
            
            logger.info(f"Text generator {self.model_name} loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading text generator {self.model_name}: {str(e)}")
            raise
    
    def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> str:
        """
        Generate text based on the given prompt.
        
        Args:
            prompt: Input text prompt
            config: Generation configuration
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        config = config or GenerationConfig()
        
        # Prepare generation config
        generation_config = GenerationConfig(
            max_length=config.max_length,
            min_length=config.min_length,
            temperature=config.temperature,
            top_p=config.top_p,
            top_k=config.top_k,
            do_sample=config.do_sample,
            num_return_sequences=config.num_return_sequences,
            repetition_penalty=config.repetition_penalty,
            length_penalty=config.length_penalty,
            no_repeat_ngram_size=config.no_repeat_ngram_size,
            early_stopping=config.early_stopping,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
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
                max_length=generation_config.max_length,
                min_length=generation_config.min_length,
                temperature=generation_config.temperature,
                top_p=generation_config.top_p,
                top_k=generation_config.top_k,
                do_sample=generation_config.do_sample,
                num_return_sequences=generation_config.num_return_sequences,
                repetition_penalty=generation_config.repetition_penalty,
                length_penalty=generation_config.length_penalty,
                no_repeat_ngram_size=generation_config.no_repeat_ngram_size,
                early_stopping=generation_config.early_stopping,
                pad_token_id=generation_config.pad_token_id,
                eos_token_id=generation_config.eos_token_id
            )
        
        # Decode output
        generated_text = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )
        
        return generated_text
    
    def generate_story(
        self,
        title: str,
        genre: str = "fiction",
        max_length: int = 500,
        **kwargs
    ) -> str:
        """
        Generate a story based on a title and genre.
        
        Args:
            title: Story title
            genre: Story genre
            max_length: Maximum length of the story
            **kwargs: Additional generation parameters
            
        Returns:
            Generated story
        """
        prompt = f"Title: {title}\nGenre: {genre}\n\nOnce upon a time,"
        
        config = GenerationConfig(
            max_length=max_length,
            temperature=0.8,
            top_p=0.9,
            repetition_penalty=1.1
        )
        
        return self.generate(prompt, config, **kwargs)
    
    def generate_poetry(
        self,
        theme: str,
        style: str = "free verse",
        max_length: int = 200,
        **kwargs
    ) -> str:
        """
        Generate poetry based on a theme and style.
        
        Args:
            theme: Poetry theme
            style: Poetry style (free verse, haiku, sonnet, etc.)
            max_length: Maximum length of the poem
            **kwargs: Additional generation parameters
            
        Returns:
            Generated poem
        """
        prompt = f"Theme: {theme}\nStyle: {style}\n\n"
        
        config = GenerationConfig(
            max_length=max_length,
            temperature=0.9,
            top_p=0.95,
            repetition_penalty=1.2
        )
        
        return self.generate(prompt, config, **kwargs)
    
    def generate_dialogue(
        self,
        character1: str,
        character2: str,
        context: str,
        max_length: int = 300,
        **kwargs
    ) -> str:
        """
        Generate dialogue between two characters.
        
        Args:
            character1: First character name
            character2: Second character name
            context: Dialogue context
            max_length: Maximum length of the dialogue
            **kwargs: Additional generation parameters
            
        Returns:
            Generated dialogue
        """
        prompt = f"Context: {context}\n\n{character1}: "
        
        config = GenerationConfig(
            max_length=max_length,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1
        )
        
        return self.generate(prompt, config, **kwargs)
    
    def complete_text(
        self,
        text: str,
        max_length: int = 100,
        **kwargs
    ) -> str:
        """
        Complete the given text.
        
        Args:
            text: Incomplete text
            max_length: Maximum length of the completion
            **kwargs: Additional generation parameters
            
        Returns:
            Completed text
        """
        config = GenerationConfig(
            max_length=max_length,
            temperature=0.6,
            top_p=0.9
        )
        
        return self.generate(text, config, **kwargs)
    
    def generate_multiple(
        self,
        prompt: str,
        num_sequences: int = 3,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> List[str]:
        """
        Generate multiple text sequences.
        
        Args:
            prompt: Input text prompt
            num_sequences: Number of sequences to generate
            config: Generation configuration
            **kwargs: Additional generation parameters
            
        Returns:
            List of generated texts
        """
        config = config or GenerationConfig()
        config.num_return_sequences = num_sequences
        
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
                max_length=config.max_length,
                min_length=config.min_length,
                temperature=config.temperature,
                top_p=config.top_p,
                top_k=config.top_k,
                do_sample=config.do_sample,
                num_return_sequences=config.num_return_sequences,
                repetition_penalty=config.repetition_penalty,
                length_penalty=config.length_penalty,
                no_repeat_ngram_size=config.no_repeat_ngram_size,
                early_stopping=config.early_stopping,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                **kwargs
            )
        
        # Decode outputs
        generated_texts = []
        for output in outputs:
            text = self.tokenizer.decode(output, skip_special_tokens=True)
            generated_texts.append(text)
        
        return generated_texts
    
    def stream_generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ):
        """
        Stream generate text token by token.
        
        Args:
            prompt: Input text prompt
            config: Generation configuration
            **kwargs: Additional generation parameters
            
        Yields:
            Generated tokens
        """
        config = config or GenerationConfig()
        
        # Tokenize input
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            truncation=True
        ).to(self.device)
        
        # Generate with streaming
        with torch.no_grad():
            for outputs in self.model.generate(
                **inputs,
                max_length=config.max_length,
                min_length=config.min_length,
                temperature=config.temperature,
                top_p=config.top_p,
                top_k=config.top_k,
                do_sample=config.do_sample,
                repetition_penalty=config.repetition_penalty,
                length_penalty=config.length_penalty,
                no_repeat_ngram_size=config.no_repeat_ngram_size,
                early_stopping=config.early_stopping,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                return_dict_in_generate=True,
                output_scores=True,
                **kwargs
            ):
                # Decode the latest token
                if hasattr(outputs, 'sequences'):
                    latest_token = outputs.sequences[0][-1:]
                    token_text = self.tokenizer.decode(latest_token, skip_special_tokens=True)
                    if token_text:
                        yield token_text
    
    def save(self, path: str):
        """Save the text generator to the specified path."""
        os.makedirs(path, exist_ok=True)
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
        
        # Save metadata
        metadata = {
            "model_name": self.model_name,
            "device": self.device
        }
        
        with open(os.path.join(path, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Text generator saved to {path}")
    
    @classmethod
    def load(cls, path: str, device: Optional[str] = None):
        """Load a saved text generator from the specified path."""
        metadata_path = os.path.join(path, "metadata.json")
        
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            
            return cls(
                model_name=path,
                device=device or metadata.get("device", "cpu")
            )
        else:
            return cls(model_name=path, device=device)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the text generator."""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "num_parameters": sum(p.numel() for p in self.model.parameters()),
            "vocab_size": self.tokenizer.vocab_size
        }