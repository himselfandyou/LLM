#!/usr/bin/env python3
"""
Basic test script to verify LLM and MCP Server installation and functionality.
"""

import sys
import os
import importlib

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")
    
    required_packages = [
        'torch',
        'transformers',
        'fastapi',
        'uvicorn',
        'pydantic',
        'sqlalchemy',
        'requests',
        'numpy',
        'sklearn'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package}")
        except ImportError as e:
            print(f"✗ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\nFailed to import: {failed_imports}")
        return False
    else:
        print("\nAll imports successful!")
        return True

def test_llm_package():
    """Test LLM package functionality."""
    print("\nTesting LLM package...")
    
    try:
        # Test imports
        from llm.models.transformer_model import TransformerModel
        from llm.models.text_classifier import TextClassifier
        from llm.models.text_generator import TextGenerator
        
        print("✓ LLM package imports successful")
        
        # Test configuration
        from llm.utils.config import Config
        config = Config(model_name="gpt2")
        print("✓ Configuration system working")
        
        # Test utilities
        from llm.utils.helpers import setup_logging, check_gpu_availability
        setup_logging()
        gpu_info = check_gpu_availability()
        print(f"✓ GPU check: {gpu_info['available']} ({gpu_info['count']} devices)")
        
        return True
        
    except Exception as e:
        print(f"✗ LLM package test failed: {e}")
        return False

def test_mcp_server_package():
    """Test MCP Server package functionality."""
    print("\nTesting MCP Server package...")
    
    try:
        # Test imports
        from mcp_server.core.config import get_settings
        from mcp_server.core.database import DatabaseManager, ModelRegistryManager
        from mcp_server.services.model_service import ModelService
        from mcp_server.services.inference_service import InferenceService
        
        print("✓ MCP Server package imports successful")
        
        # Test configuration
        settings = get_settings()
        print(f"✓ Configuration loaded: {settings.host}:{settings.port}")
        
        return True
        
    except Exception as e:
        print(f"✗ MCP Server package test failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without loading large models."""
    print("\nTesting basic functionality...")
    
    try:
        # Test text generation (without loading model)
        from llm.models.text_generator import TextGenerator
        
        # This will fail if transformers is not properly installed
        # but we can catch the error gracefully
        try:
            generator = TextGenerator("gpt2")
            print("✓ Text generator initialized")
        except Exception as e:
            print(f"⚠ Text generator initialization failed (expected if no internet): {e}")
        
        # Test configuration system
        from llm.utils.config import Config
        config = Config(
            model_name="test-model",
            task_type="text-generation",
            max_length=100,
            temperature=0.7
        )
        print("✓ Configuration system working")
        
        # Test helper functions
        from llm.utils.helpers import format_model_size, set_random_seed
        size_str = format_model_size(1024 * 1024)  # 1MB
        print(f"✓ Size formatting: {size_str}")
        
        set_random_seed(42)
        print("✓ Random seed setting working")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("LLM and MCP Server Basic Test")
    print("=" * 40)
    
    tests = [
        ("Package Imports", test_imports),
        ("LLM Package", test_llm_package),
        ("MCP Server Package", test_mcp_server_package),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("Test Summary:")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your installation is working correctly.")
        print("\nNext steps:")
        print("1. Run 'python example.py' to see the full demo")
        print("2. Run 'python main.py' to start the MCP Server")
        print("3. Visit http://localhost:8000/docs for API documentation")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check that you have Python 3.8+ installed")
        print("3. For GPU support, ensure PyTorch is installed with CUDA support")

if __name__ == "__main__":
    main()