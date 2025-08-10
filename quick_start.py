#!/usr/bin/env python3
"""
Quick Start Guide for the LLM and MCP Server System

This script demonstrates the key features and how to use them.
"""

import sys
import os

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section."""
    print(f"\n📋 {title}")
    print("-" * 40)

def demo_direct_llm_usage():
    """Demonstrate direct LLM package usage."""
    print_section("Direct LLM Package Usage")
    
    try:
        from llm.models.text_generator import TextGenerator
        from llm.models.text_classifier import TextClassifier
        
        print("✅ LLM package imported successfully")
        
        # Text generation example
        print("\n🔤 Text Generation Example:")
        generator = TextGenerator("gpt2")
        result = generator.generate("The future of AI is", max_length=50)
        print(f"Prompt: 'The future of AI is'")
        print(f"Generated: {result}")
        
        # Text classification example
        print("\n🏷️ Text Classification Example:")
        classifier = TextClassifier("distilbert-base-uncased-finetuned-sst-2-english")
        result = classifier.classify("I love this amazing technology!")
        print(f"Text: 'I love this amazing technology!'")
        print(f"Classification: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in direct LLM usage: {e}")
        return False

def demo_api_usage():
    """Demonstrate API usage."""
    print_section("API Usage")
    
    try:
        import requests
        
        base_url = "http://localhost:8001"
        
        # Check if server is running
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            
            # Test text generation via API
            print("\n🔤 Text Generation via API:")
            response = requests.post(f"{base_url}/generate", 
                json={"prompt": "Hello world", "max_length": 30})
            if response.status_code == 200:
                result = response.json()
                print(f"Generated: {result['generated_text']}")
                print(f"Processing time: {result['processing_time_ms']}ms")
            
            # Test text classification via API
            print("\n🏷️ Text Classification via API:")
            response = requests.post(f"{base_url}/classify", 
                json={"text": "This is wonderful!"})
            if response.status_code == 200:
                result = response.json()
                print(f"Classification: {result['classification']}")
                print(f"Processing time: {result['processing_time_ms']}ms")
            
            return True
        else:
            print("❌ Server is not running")
            return False
            
    except Exception as e:
        print(f"❌ Error in API usage: {e}")
        return False

def show_usage_examples():
    """Show usage examples."""
    print_section("Usage Examples")
    
    print("1. Direct LLM Usage:")
    print("""
from llm.models.text_generator import TextGenerator
from llm.models.text_classifier import TextClassifier

# Text generation
generator = TextGenerator("gpt2")
text = generator.generate("Your prompt here", max_length=100)

# Text classification
classifier = TextClassifier("distilbert-base-uncased-finetuned-sst-2-english")
result = classifier.classify("Your text here")
""")
    
    print("\n2. API Usage:")
    print("""
import requests

# Text generation
response = requests.post("http://localhost:8001/generate", 
    json={"prompt": "Your prompt", "max_length": 100})
result = response.json()

# Text classification
response = requests.post("http://localhost:8001/classify", 
    json={"text": "Your text"})
result = response.json()
""")
    
    print("\n3. Available Models:")
    print("""
Text Generation Models:
- gpt2 (default)
- gpt2-medium
- gpt2-large
- gpt2-xl

Text Classification Models:
- distilbert-base-uncased-finetuned-sst-2-english (default)
- bert-base-uncased
- roberta-base
""")

def show_next_steps():
    """Show next steps for users."""
    print_section("Next Steps")
    
    print("🚀 What you can do now:")
    print("1. Use the LLM package directly in your Python code")
    print("2. Start the server: python simple_server.py")
    print("3. Access the API at: http://localhost:8001")
    print("4. View API docs at: http://localhost:8001/docs")
    print("5. Run the client example: python client_example.py")
    
    print("\n🔧 Advanced Features:")
    print("1. Fine-tune models on your own data")
    print("2. Add new model types (summarization, translation, etc.)")
    print("3. Deploy with Docker using the provided Dockerfile")
    print("4. Scale with the full MCP Server implementation")
    
    print("\n📚 Learning Resources:")
    print("1. Check the README.md for detailed documentation")
    print("2. Explore the notebooks/ directory for examples")
    print("3. Review the test files for usage patterns")
    print("4. Examine the source code for implementation details")

def main():
    """Main function."""
    print_header("LLM and MCP Server System - Quick Start Guide")
    
    print("🎉 Welcome to the LLM and MCP Server System!")
    print("This system provides both direct Python API and REST API access to language models.")
    
    # Test direct LLM usage
    direct_success = demo_direct_llm_usage()
    
    # Test API usage
    api_success = demo_api_usage()
    
    # Show usage examples
    show_usage_examples()
    
    # Show next steps
    show_next_steps()
    
    # Summary
    print_header("Summary")
    
    if direct_success and api_success:
        print("✅ All systems are working correctly!")
        print("🎯 You're ready to start using the LLM system!")
    elif direct_success:
        print("✅ Direct LLM usage is working!")
        print("⚠️ API server needs to be started: python simple_server.py")
    else:
        print("❌ Some components need attention.")
        print("🔧 Check the installation and try running the tests again.")
    
    print("\nHappy coding! 🚀")

if __name__ == "__main__":
    main()