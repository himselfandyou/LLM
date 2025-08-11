"""
Advanced Large Language Model Implementation

A complete transformer-based language model implementation from scratch,
including attention mechanisms, positional encoding, and training capabilities.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import numpy as np
from typing import Optional, Tuple, List, Dict, Any
import logging
from dataclasses import dataclass
import json
import os

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for the language model."""
    vocab_size: int = 50257
    max_seq_length: int = 1024
    hidden_size: int = 768
    num_layers: int = 12
    num_attention_heads: int = 12
    intermediate_size: int = 3072
    dropout: float = 0.1
    layer_norm_eps: float = 1e-12
    initializer_range: float = 0.02
    pad_token_id: int = 0
    bos_token_id: int = 1
    eos_token_id: int = 2

class PositionalEncoding(nn.Module):
    """Positional encoding for transformer models."""
    
    def __init__(self, hidden_size: int, max_seq_length: int, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        pe = torch.zeros(max_seq_length, hidden_size)
        position = torch.arange(0, max_seq_length, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, hidden_size, 2).float() * 
                           (-math.log(10000.0) / hidden_size))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)

class MultiHeadAttention(nn.Module):
    """Multi-head self-attention mechanism."""
    
    def __init__(self, hidden_size: int, num_attention_heads: int, dropout: float = 0.1):
        super().__init__()
        self.num_attention_heads = num_attention_heads
        self.attention_head_size = int(hidden_size / num_attention_heads)
        self.all_head_size = self.num_attention_heads * self.attention_head_size
        
        self.query = nn.Linear(hidden_size, self.all_head_size)
        self.key = nn.Linear(hidden_size, self.all_head_size)
        self.value = nn.Linear(hidden_size, self.all_head_size)
        self.dropout = nn.Dropout(dropout)
        self.output = nn.Linear(hidden_size, hidden_size)
        self.output_dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(hidden_size, eps=1e-12)
    
    def transpose_for_scores(self, x: torch.Tensor) -> torch.Tensor:
        new_x_shape = x.size()[:-1] + (self.num_attention_heads, self.attention_head_size)
        x = x.view(*new_x_shape)
        return x.permute(0, 2, 1, 3)
    
    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        past_key_value: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
        output_attentions: bool = False
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor, torch.Tensor]]]:
        
        residual = hidden_states
        
        # Apply layer norm
        hidden_states = self.layer_norm(hidden_states)
        
        mixed_query_layer = self.query(hidden_states)
        mixed_key_layer = self.key(hidden_states)
        mixed_value_layer = self.value(hidden_states)
        
        query_layer = self.transpose_for_scores(mixed_query_layer)
        key_layer = self.transpose_for_scores(mixed_key_layer)
        value_layer = self.transpose_for_scores(mixed_value_layer)
        
        # Handle past key/value states
        if past_key_value is not None:
            key_layer = torch.cat([past_key_value[0], key_layer], dim=2)
            value_layer = torch.cat([past_key_value[1], value_layer], dim=2)
        
        present_key_value = (key_layer, value_layer)
        
        # Compute attention scores
        attention_scores = torch.matmul(query_layer, key_layer.transpose(-1, -2))
        attention_scores = attention_scores / math.sqrt(self.attention_head_size)
        
        if attention_mask is not None:
            attention_scores = attention_scores + attention_mask
        
        attention_probs = F.softmax(attention_scores, dim=-1)
        attention_probs = self.dropout(attention_probs)
        
        context_layer = torch.matmul(attention_probs, value_layer)
        context_layer = context_layer.permute(0, 2, 1, 3).contiguous()
        new_context_layer_shape = context_layer.size()[:-2] + (self.all_head_size,)
        context_layer = context_layer.view(*new_context_layer_shape)
        
        output = self.output(context_layer)
        output = self.output_dropout(output)
        
        # Add residual connection
        output = output + residual
        
        outputs = (output,)
        if output_attentions:
            outputs += (attention_probs,)
        if past_key_value is not None:
            outputs += (present_key_value,)
        
        return outputs

class FeedForward(nn.Module):
    """Feed-forward network for transformer blocks."""
    
    def __init__(self, hidden_size: int, intermediate_size: int, dropout: float = 0.1):
        super().__init__()
        self.dense_h_to_4h = nn.Linear(hidden_size, intermediate_size)
        self.dense_4h_to_h = nn.Linear(intermediate_size, hidden_size)
        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(hidden_size, eps=1e-12)
        self.activation = nn.GELU()
    
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        residual = hidden_states
        
        # Apply layer norm
        hidden_states = self.layer_norm(hidden_states)
        
        hidden_states = self.dense_h_to_4h(hidden_states)
        hidden_states = self.activation(hidden_states)
        hidden_states = self.dense_4h_to_h(hidden_states)
        hidden_states = self.dropout(hidden_states)
        
        # Add residual connection
        hidden_states = hidden_states + residual
        
        return hidden_states

class TransformerBlock(nn.Module):
    """A single transformer block with attention and feed-forward layers."""
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.attention = MultiHeadAttention(
            config.hidden_size,
            config.num_attention_heads,
            config.dropout
        )
        self.feed_forward = FeedForward(
            config.hidden_size,
            config.intermediate_size,
            config.dropout
        )
    
    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        past_key_value: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
        output_attentions: bool = False
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor, torch.Tensor]]]:
        
        attention_outputs = self.attention(
            hidden_states,
            attention_mask=attention_mask,
            past_key_value=past_key_value,
            output_attentions=output_attentions
        )
        
        attention_output = attention_outputs[0]
        feed_forward_output = self.feed_forward(attention_output)
        
        outputs = (feed_forward_output,)
        if len(attention_outputs) > 1:
            outputs += attention_outputs[1:]
        
        return outputs

class AdvancedLLM(nn.Module):
    """
    Advanced Large Language Model implementation.
    
    A complete transformer-based language model with:
    - Multi-head self-attention
    - Positional encoding
    - Layer normalization
    - Residual connections
    - Configurable architecture
    """
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        
        # Token embedding
        self.embedding = nn.Embedding(config.vocab_size, config.hidden_size)
        
        # Positional encoding
        self.positional_encoding = PositionalEncoding(
            config.hidden_size,
            config.max_seq_length,
            config.dropout
        )
        
        # Transformer blocks
        self.layers = nn.ModuleList([
            TransformerBlock(config) for _ in range(config.num_layers)
        ])
        
        # Final layer norm
        self.final_layer_norm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        
        # Output projection
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        
        # Initialize weights
        self.apply(self._init_weights)
        
        # Tie weights between embedding and output layer
        self.lm_head.weight = self.embedding.weight
    
    def _init_weights(self, module):
        """Initialize the weights of the model."""
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
    
    def get_input_embeddings(self):
        return self.embedding
    
    def set_input_embeddings(self, value):
        self.embedding = value
    
    def forward(
        self,
        input_ids: torch.LongTensor,
        attention_mask: Optional[torch.Tensor] = None,
        past_key_values: Optional[List[Tuple[torch.Tensor, torch.Tensor]]] = None,
        position_ids: Optional[torch.LongTensor] = None,
        output_attentions: bool = False,
        output_hidden_states: bool = False,
        return_dict: bool = True
    ) -> Dict[str, torch.Tensor]:
        
        batch_size, seq_length = input_ids.shape
        
        if attention_mask is None:
            attention_mask = torch.ones((batch_size, seq_length), device=input_ids.device)
        
        if position_ids is None:
            position_ids = torch.arange(seq_length, dtype=torch.long, device=input_ids.device)
            position_ids = position_ids.unsqueeze(0).expand_as(input_ids)
        
        # Create causal attention mask
        causal_mask = torch.triu(
            torch.ones((seq_length, seq_length), device=input_ids.device),
            diagonal=1
        ).bool()
        causal_mask = causal_mask.unsqueeze(0).unsqueeze(0)
        
        # Combine attention masks
        attention_mask = attention_mask.unsqueeze(1).unsqueeze(2)
        attention_mask = attention_mask.to(dtype=torch.float32)
        attention_mask = (1.0 - attention_mask) * -10000.0
        
        # Get embeddings
        hidden_states = self.embedding(input_ids)
        hidden_states = self.positional_encoding(hidden_states.transpose(0, 1)).transpose(0, 1)
        
        all_hidden_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        next_cache = () if past_key_values is not None else None
        
        for i, layer in enumerate(self.layers):
            if output_hidden_states:
                all_hidden_states = all_hidden_states + (hidden_states,)
            
            past_key_value = past_key_values[i] if past_key_values is not None else None
            
            layer_outputs = layer(
                hidden_states,
                attention_mask=attention_mask,
                past_key_value=past_key_value,
                output_attentions=output_attentions
            )
            
            hidden_states = layer_outputs[0]
            
            if output_attentions:
                all_attentions = all_attentions + (layer_outputs[1],)
            
            if past_key_values is not None:
                next_cache = next_cache + (layer_outputs[-1],)
        
        hidden_states = self.final_layer_norm(hidden_states)
        
        if output_hidden_states:
            all_hidden_states = all_hidden_states + (hidden_states,)
        
        logits = self.lm_head(hidden_states)
        
        return {
            "logits": logits,
            "hidden_states": all_hidden_states,
            "attentions": all_attentions,
            "past_key_values": next_cache
        }
    
    def generate(
        self,
        input_ids: torch.LongTensor,
        max_length: int = 100,
        temperature: float = 1.0,
        top_k: int = 50,
        top_p: float = 0.9,
        do_sample: bool = True,
        pad_token_id: Optional[int] = None,
        eos_token_id: Optional[int] = None,
        repetition_penalty: float = 1.0
    ) -> torch.LongTensor:
        """
        Generate text using the language model.
        
        Args:
            input_ids: Input token IDs
            max_length: Maximum length of generated sequence
            temperature: Sampling temperature
            top_k: Top-k sampling parameter
            top_p: Top-p (nucleus) sampling parameter
            do_sample: Whether to use sampling
            pad_token_id: Padding token ID
            eos_token_id: End-of-sequence token ID
            repetition_penalty: Penalty for repetition
            
        Returns:
            Generated token IDs
        """
        pad_token_id = pad_token_id or self.config.pad_token_id
        eos_token_id = eos_token_id or self.config.eos_token_id
        
        batch_size = input_ids.shape[0]
        current_length = input_ids.shape[1]
        
        # Initialize past key values for efficient generation
        past_key_values = None
        
        generated = input_ids.clone()
        
        for _ in range(max_length - current_length):
            # Get model outputs
            outputs = self.forward(
                input_ids=generated,
                past_key_values=past_key_values,
                return_dict=True
            )
            
            logits = outputs["logits"][:, -1, :] / temperature
            past_key_values = outputs["past_key_values"]
            
            # Apply repetition penalty
            if repetition_penalty != 1.0:
                for i in range(batch_size):
                    for previous_token in set(generated[i].tolist()):
                        if previous_token != pad_token_id:
                            logits[i, previous_token] /= repetition_penalty
            
            # Apply top-k filtering
            if top_k > 0:
                indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
                logits[indices_to_remove] = -float('Inf')
            
            # Apply top-p (nucleus) filtering
            if top_p < 1.0:
                sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                
                sorted_indices_to_remove = cumulative_probs > top_p
                sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                sorted_indices_to_remove[..., 0] = 0
                
                indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                logits[indices_to_remove] = -float('Inf')
            
            # Sample next token
            if do_sample:
                probs = F.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
            else:
                next_token = torch.argmax(logits, dim=-1, keepdim=True)
            
            # Append to generated sequence
            generated = torch.cat([generated, next_token], dim=-1)
            
            # Check for EOS token
            if eos_token_id is not None and (next_token == eos_token_id).any():
                break
        
        return generated
    
    def save_pretrained(self, save_directory: str):
        """Save the model to a directory."""
        os.makedirs(save_directory, exist_ok=True)
        
        # Save model weights
        torch.save(self.state_dict(), os.path.join(save_directory, "pytorch_model.bin"))
        
        # Save configuration
        config_dict = {
            "vocab_size": self.config.vocab_size,
            "max_seq_length": self.config.max_seq_length,
            "hidden_size": self.config.hidden_size,
            "num_layers": self.config.num_layers,
            "num_attention_heads": self.config.num_attention_heads,
            "intermediate_size": self.config.intermediate_size,
            "dropout": self.config.dropout,
            "layer_norm_eps": self.config.layer_norm_eps,
            "initializer_range": self.config.initializer_range,
            "pad_token_id": self.config.pad_token_id,
            "bos_token_id": self.config.bos_token_id,
            "eos_token_id": self.config.eos_token_id
        }
        
        with open(os.path.join(save_directory, "config.json"), "w") as f:
            json.dump(config_dict, f, indent=2)
        
        logger.info(f"Model saved to {save_directory}")
    
    @classmethod
    def from_pretrained(cls, model_directory: str, **kwargs):
        """Load a model from a directory."""
        config_path = os.path.join(model_directory, "config.json")
        model_path = os.path.join(model_directory, "pytorch_model.bin")
        
        if not os.path.exists(config_path):
            raise ValueError(f"Config file not found at {config_path}")
        
        with open(config_path, "r") as f:
            config_dict = json.load(f)
        
        config = ModelConfig(**config_dict)
        model = cls(config, **kwargs)
        
        if os.path.exists(model_path):
            model.load_state_dict(torch.load(model_path, map_location="cpu"))
            logger.info(f"Model loaded from {model_directory}")
        
        return model

class LLMTrainer:
    """Trainer class for the language model."""
    
    def __init__(
        self,
        model: AdvancedLLM,
        tokenizer,
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        self.model = model.to(device)
        self.tokenizer = tokenizer
        self.device = device
        self.optimizer = None
        self.scheduler = None
    
    def setup_training(
        self,
        learning_rate: float = 5e-5,
        weight_decay: float = 0.01,
        warmup_steps: int = 1000,
        total_steps: int = 100000
    ):
        """Setup optimizer and scheduler for training."""
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )
        
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer,
            T_max=total_steps,
            eta_min=learning_rate * 0.1
        )
    
    def train_step(self, batch: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """Perform a single training step."""
        self.model.train()
        
        input_ids = batch["input_ids"].to(self.device)
        attention_mask = batch.get("attention_mask", None)
        if attention_mask is not None:
            attention_mask = attention_mask.to(self.device)
        
        # Forward pass
        outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        logits = outputs["logits"]
        
        # Calculate loss (shifted language modeling)
        shift_logits = logits[..., :-1, :].contiguous()
        shift_labels = input_ids[..., 1:].contiguous()
        
        loss_fct = nn.CrossEntropyLoss()
        loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
        
        # Backward pass
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
        self.optimizer.step()
        self.scheduler.step()
        
        return {"loss": loss.item()}
    
    def evaluate(self, eval_dataloader) -> Dict[str, float]:
        """Evaluate the model on validation data."""
        self.model.eval()
        total_loss = 0.0
        num_batches = 0
        
        with torch.no_grad():
            for batch in eval_dataloader:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch.get("attention_mask", None)
                if attention_mask is not None:
                    attention_mask = attention_mask.to(self.device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )
                
                logits = outputs["logits"]
                shift_logits = logits[..., :-1, :].contiguous()
                shift_labels = input_ids[..., 1:].contiguous()
                
                loss_fct = nn.CrossEntropyLoss()
                loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
                
                total_loss += loss.item()
                num_batches += 1
        
        return {"eval_loss": total_loss / num_batches}