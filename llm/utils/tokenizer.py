"""
Custom Tokenizer Implementation

A simple but effective tokenizer for the language model.
"""

import re
import json
import os
from typing import List, Dict, Optional, Tuple, Union
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class SimpleTokenizer:
    """
    A simple tokenizer implementation for the language model.
    
    Features:
    - Byte-pair encoding (BPE) inspired tokenization
    - Vocabulary management
    - Special tokens support
    - Encoding/decoding capabilities
    """
    
    def __init__(
        self,
        vocab_size: int = 50257,
        min_freq: int = 2,
        special_tokens: Optional[Dict[str, int]] = None
    ):
        self.vocab_size = vocab_size
        self.min_freq = min_freq
        self.special_tokens = special_tokens or {
            "<pad>": 0,
            "<bos>": 1,
            "<eos>": 2,
            "<unk>": 3
        }
        
        self.vocab = {}
        self.reverse_vocab = {}
        self.merges = {}
        self.pattern = re.compile(r'\S+|\n')
        
        # Initialize with special tokens
        for token, idx in self.special_tokens.items():
            self.vocab[token] = idx
            self.reverse_vocab[idx] = token
    
    def train(self, texts: List[str]):
        """
        Train the tokenizer on a list of texts.
        
        Args:
            texts: List of training texts
        """
        logger.info("Training tokenizer...")
        
        # Count character pairs
        pair_counts = Counter()
        word_counts = Counter()
        
        for text in texts:
            words = self.pattern.findall(text)
            for word in words:
                word_counts[word] += 1
                if len(word) > 1:
                    pairs = self._get_pairs(word)
                    for pair in pairs:
                        pair_counts[pair] += word_counts[word]
        
        # Build vocabulary
        vocab_size = self.vocab_size - len(self.special_tokens)
        current_vocab_size = len(self.special_tokens)
        
        # Add single characters first
        char_counts = Counter()
        for word, count in word_counts.items():
            for char in word:
                char_counts[char] += count
        
        # Add most frequent characters
        for char, count in char_counts.most_common(vocab_size // 2):
            if current_vocab_size >= self.vocab_size:
                break
            if char not in self.vocab:
                self.vocab[char] = current_vocab_size
                self.reverse_vocab[current_vocab_size] = char
                current_vocab_size += 1
        
        # Add most frequent pairs
        for pair, count in pair_counts.most_common():
            if current_vocab_size >= self.vocab_size:
                break
            if pair not in self.vocab:
                self.vocab[pair] = current_vocab_size
                self.reverse_vocab[current_vocab_size] = pair
                current_vocab_size += 1
        
        logger.info(f"Tokenizer trained with {len(self.vocab)} tokens")
    
    def _get_pairs(self, word: str) -> List[Tuple[str, str]]:
        """Get character pairs from a word."""
        pairs = []
        prev_char = word[0]
        for char in word[1:]:
            pairs.append((prev_char, char))
            prev_char = char
        return pairs
    
    def encode(self, text: str) -> List[int]:
        """
        Encode text to token IDs.
        
        Args:
            text: Input text
            
        Returns:
            List of token IDs
        """
        tokens = []
        words = self.pattern.findall(text)
        
        for word in words:
            if word in self.vocab:
                tokens.append(self.vocab[word])
            else:
                # Try to tokenize unknown word
                word_tokens = self._tokenize_word(word)
                tokens.extend(word_tokens)
        
        return tokens
    
    def _tokenize_word(self, word: str) -> List[int]:
        """Tokenize an unknown word using greedy matching."""
        tokens = []
        start = 0
        
        while start < len(word):
            end = len(word)
            found = False
            
            while end > start:
                substr = word[start:end]
                if substr in self.vocab:
                    tokens.append(self.vocab[substr])
                    found = True
                    break
                end -= 1
            
            if not found:
                # Use unknown token
                tokens.append(self.special_tokens["<unk>"])
                start += 1
            else:
                start = end
        
        return tokens
    
    def decode(self, token_ids: List[int]) -> str:
        """
        Decode token IDs back to text.
        
        Args:
            token_ids: List of token IDs
            
        Returns:
            Decoded text
        """
        tokens = []
        for token_id in token_ids:
            if token_id in self.reverse_vocab:
                tokens.append(self.reverse_vocab[token_id])
            else:
                tokens.append(self.reverse_vocab[self.special_tokens["<unk>"]])
        
        return "".join(tokens)
    
    def encode_batch(self, texts: List[str], padding: bool = True, truncation: bool = True, max_length: Optional[int] = None) -> Dict[str, List[List[int]]]:
        """
        Encode a batch of texts.
        
        Args:
            texts: List of input texts
            padding: Whether to pad sequences
            truncation: Whether to truncate sequences
            max_length: Maximum sequence length
            
        Returns:
            Dictionary with 'input_ids' and 'attention_mask'
        """
        encoded = [self.encode(text) for text in texts]
        
        if max_length is None:
            max_length = max(len(seq) for seq in encoded) if encoded else 0
        
        if truncation:
            encoded = [seq[:max_length] for seq in encoded]
        
        if padding:
            max_len = max(len(seq) for seq in encoded) if encoded else 0
            attention_mask = []
            
            for i, seq in enumerate(encoded):
                if len(seq) < max_len:
                    encoded[i] = seq + [self.special_tokens["<pad>"]] * (max_len - len(seq))
                attention_mask.append([1] * len(seq) + [0] * (max_len - len(seq)))
        else:
            attention_mask = [[1] * len(seq) for seq in encoded]
        
        return {
            "input_ids": encoded,
            "attention_mask": attention_mask
        }
    
    def save(self, path: str):
        """Save the tokenizer to a file."""
        os.makedirs(path, exist_ok=True)
        
        tokenizer_data = {
            "vocab": self.vocab,
            "special_tokens": self.special_tokens,
            "vocab_size": self.vocab_size,
            "min_freq": self.min_freq
        }
        
        with open(os.path.join(path, "tokenizer.json"), "w") as f:
            json.dump(tokenizer_data, f, indent=2)
        
        logger.info(f"Tokenizer saved to {path}")
    
    @classmethod
    def load(cls, path: str):
        """Load a tokenizer from a file."""
        tokenizer_path = os.path.join(path, "tokenizer.json")
        
        if not os.path.exists(tokenizer_path):
            raise ValueError(f"Tokenizer file not found at {tokenizer_path}")
        
        with open(tokenizer_path, "r") as f:
            tokenizer_data = json.load(f)
        
        tokenizer = cls(
            vocab_size=tokenizer_data["vocab_size"],
            min_freq=tokenizer_data["min_freq"],
            special_tokens=tokenizer_data["special_tokens"]
        )
        
        tokenizer.vocab = tokenizer_data["vocab"]
        tokenizer.reverse_vocab = {int(k): v for k, v in tokenizer.vocab.items()}
        
        logger.info(f"Tokenizer loaded from {path}")
        return tokenizer

class GPT2Tokenizer:
    """
    A simplified GPT-2 style tokenizer using byte-pair encoding.
    """
    
    def __init__(self, vocab_size: int = 50257):
        self.vocab_size = vocab_size
        self.special_tokens = {
            "<|endoftext|>": 50256,
            "<|pad|>": 50257
        }
        
        # Initialize with basic vocabulary
        self.vocab = {}
        self.reverse_vocab = {}
        
        # Add byte-level tokens
        for i in range(256):
            self.vocab[bytes([i]).decode('latin-1')] = i
            self.reverse_vocab[i] = bytes([i]).decode('latin-1')
        
        # Add special tokens
        for token, idx in self.special_tokens.items():
            if idx < vocab_size:
                self.vocab[token] = idx
                self.reverse_vocab[idx] = token
    
    def encode(self, text: str) -> List[int]:
        """Encode text using byte-pair encoding."""
        # Simple byte-level encoding for now
        tokens = []
        for char in text:
            if char in self.vocab:
                tokens.append(self.vocab[char])
            else:
                # Fallback to unknown token
                tokens.append(self.special_tokens.get("<|pad|>", 0))
        
        return tokens
    
    def decode(self, token_ids: List[int]) -> str:
        """Decode token IDs back to text."""
        text = ""
        for token_id in token_ids:
            if token_id in self.reverse_vocab:
                text += self.reverse_vocab[token_id]
        
        return text
    
    def encode_batch(self, texts: List[str], padding: bool = True, truncation: bool = True, max_length: Optional[int] = None) -> Dict[str, List[List[int]]]:
        """Encode a batch of texts."""
        encoded = [self.encode(text) for text in texts]
        
        if max_length is None:
            max_length = max(len(seq) for seq in encoded) if encoded else 0
        
        if truncation:
            encoded = [seq[:max_length] for seq in encoded]
        
        if padding:
            max_len = max(len(seq) for seq in encoded) if encoded else 0
            attention_mask = []
            
            for i, seq in enumerate(encoded):
                if len(seq) < max_len:
                    encoded[i] = seq + [self.special_tokens["<|pad|>"]] * (max_len - len(seq))
                attention_mask.append([1] * len(seq) + [0] * (max_len - len(seq)))
        else:
            attention_mask = [[1] * len(seq) for seq in encoded]
        
        return {
            "input_ids": encoded,
            "attention_mask": attention_mask
        }