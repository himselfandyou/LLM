"""
Dataset utilities for language model training.
"""

import torch
from torch.utils.data import Dataset, DataLoader
from typing import List, Dict, Optional, Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)

class TextDataset(Dataset):
    """Dataset for text data."""
    
    def __init__(self, texts: List[str], tokenizer, max_length: int = 512):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Tokenize all texts
        self.encoded_texts = []
        for text in texts:
            tokens = tokenizer.encode(text)
            if len(tokens) > max_length:
                # Split long sequences
                for i in range(0, len(tokens), max_length):
                    chunk = tokens[i:i + max_length]
                    if len(chunk) >= 10:  # Minimum sequence length
                        self.encoded_texts.append(chunk)
            else:
                self.encoded_texts.append(tokens)
    
    def __len__(self):
        return len(self.encoded_texts)
    
    def __getitem__(self, idx):
        tokens = self.encoded_texts[idx]
        
        # Pad or truncate to max_length
        if len(tokens) < self.max_length:
            tokens = tokens + [0] * (self.max_length - len(tokens))
        else:
            tokens = tokens[:self.max_length]
        
        return {
            "input_ids": torch.tensor(tokens, dtype=torch.long),
            "attention_mask": torch.tensor([1] * len(tokens), dtype=torch.long)
        }

def create_dataloader(
    texts: List[str],
    tokenizer,
    batch_size: int = 8,
    max_length: int = 512,
    shuffle: bool = True
) -> DataLoader:
    """Create a DataLoader for training."""
    dataset = TextDataset(texts, tokenizer, max_length)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)