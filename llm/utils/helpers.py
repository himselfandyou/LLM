"""
Helper utilities for the LLM package.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import torch
import numpy as np

logger = logging.getLogger(__name__)

def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration."""
    log_level = getattr(logging, level.upper())
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

def get_model_size(model: torch.nn.Module) -> Dict[str, Any]:
    """Get model size information."""
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    # Estimate memory usage
    param_size = 0
    buffer_size = 0
    
    for param in model.parameters():
        param_size += param.nelement() * param.element_size()
    
    for buffer in model.buffers():
        buffer_size += buffer.nelement() * buffer.element_size()
    
    size_all_mb = (param_size + buffer_size) / 1024**2
    
    return {
        "total_parameters": total_params,
        "trainable_parameters": trainable_params,
        "memory_usage_mb": size_all_mb,
        "memory_usage_gb": size_all_mb / 1024
    }

def save_model_metadata(model_info: Dict[str, Any], file_path: str):
    """Save model metadata to file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w') as f:
        json.dump(model_info, f, indent=2)
    
    logger.info(f"Model metadata saved to {file_path}")

def load_model_metadata(file_path: str) -> Dict[str, Any]:
    """Load model metadata from file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Metadata file not found: {file_path}")
    
    with open(file_path, 'r') as f:
        metadata = json.load(f)
    
    return metadata

def validate_model_path(model_path: str) -> bool:
    """Validate that a model path exists and contains required files."""
    if not os.path.exists(model_path):
        return False
    
    # Check for common model files
    required_files = ["config.json"]
    optional_files = ["pytorch_model.bin", "model.safetensors", "tokenizer.json"]
    
    # Check required files
    for file_name in required_files:
        if not os.path.exists(os.path.join(model_path, file_name)):
            return False
    
    # Check at least one model file exists
    model_files_exist = any(
        os.path.exists(os.path.join(model_path, file_name))
        for file_name in optional_files
    )
    
    return model_files_exist

def format_model_size(size_bytes: int) -> str:
    """Format model size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def calculate_metrics(predictions: List[Any], targets: List[Any]) -> Dict[str, float]:
    """Calculate basic metrics for model evaluation."""
    if len(predictions) != len(targets):
        raise ValueError("Predictions and targets must have the same length")
    
    # Calculate accuracy
    correct = sum(1 for p, t in zip(predictions, targets) if p == t)
    accuracy = correct / len(predictions)
    
    return {
        "accuracy": accuracy,
        "total_samples": len(predictions),
        "correct_predictions": correct
    }

def create_model_summary(model: torch.nn.Module, input_shape: tuple = None) -> Dict[str, Any]:
    """Create a summary of the model architecture."""
    summary = {
        "model_type": type(model).__name__,
        "device": next(model.parameters()).device,
        "dtype": next(model.parameters()).dtype,
        "layers": []
    }
    
    # Get model size info
    size_info = get_model_size(model)
    summary.update(size_info)
    
    # Add layer information
    for name, module in model.named_modules():
        if len(list(module.children())) == 0:  # Leaf modules only
            layer_info = {
                "name": name,
                "type": type(module).__name__,
                "parameters": sum(p.numel() for p in module.parameters())
            }
            summary["layers"].append(layer_info)
    
    return summary

def set_random_seed(seed: int = 42):
    """Set random seed for reproducibility."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    
    logger.info(f"Random seed set to {seed}")

def check_gpu_availability() -> Dict[str, Any]:
    """Check GPU availability and information."""
    gpu_info = {
        "available": torch.cuda.is_available(),
        "count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "devices": []
    }
    
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            device_info = {
                "index": i,
                "name": torch.cuda.get_device_name(i),
                "memory_total_gb": torch.cuda.get_device_properties(i).total_memory / 1024**3,
                "memory_allocated_gb": torch.cuda.memory_allocated(i) / 1024**3,
                "memory_cached_gb": torch.cuda.memory_reserved(i) / 1024**3
            }
            gpu_info["devices"].append(device_info)
    
    return gpu_info

def cleanup_gpu_memory():
    """Clean up GPU memory."""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        logger.info("GPU memory cleaned up")

def get_optimal_batch_size(model: torch.nn.Module, max_memory_gb: float = 8.0) -> int:
    """Estimate optimal batch size based on available memory."""
    if not torch.cuda.is_available():
        return 8  # Default for CPU
    
    # Get model size
    size_info = get_model_size(model)
    model_memory_gb = size_info["memory_usage_gb"]
    
    # Estimate memory per sample (rough approximation)
    memory_per_sample_gb = model_memory_gb * 0.1  # 10% of model size per sample
    
    # Calculate optimal batch size
    available_memory_gb = max_memory_gb - model_memory_gb
    optimal_batch_size = max(1, int(available_memory_gb / memory_per_sample_gb))
    
    # Cap at reasonable maximum
    optimal_batch_size = min(optimal_batch_size, 32)
    
    logger.info(f"Estimated optimal batch size: {optimal_batch_size}")
    return optimal_batch_size