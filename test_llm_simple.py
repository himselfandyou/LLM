#!/usr/bin/env python3
"""
Simple test script to verify LLM functionality.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_text_generation():
    """Test basic text generation."""
    print("Testing text generation...")
    
    try:
        from llm.models.text_generator import TextGenerator
        
        # Initialize generator
        print("Initializing text generator...")
        generator = TextGenerator("gpt2")
        
        # Generate text
        prompt = "Hello, how are you?"
        print(f"Generating text for prompt: '{prompt}'")
        
        result = generator.generate(
            prompt=prompt,
            max_length=50,
            temperature=0.7
        )
        
        print(f"Generated text: {result}")
        print("✅ Text generation successful!")
        
        return True
        
    except Exception as e:
        print(f"❌ Text generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_text_classification():
    """Test basic text classification."""
    print("\nTesting text classification...")
    
    try:
        from llm.models.text_classifier import TextClassifier
        
        # Initialize classifier
        print("Initializing text classifier...")
        classifier = TextClassifier("distilbert-base-uncased-finetuned-sst-2-english")
        
        # Classify text
        text = "I love this movie! It's amazing!"
        print(f"Classifying text: '{text}'")
        
        result = classifier.classify(text)
        print(f"Classification result: {result}")
        print("✅ Text classification successful!")
        
        return True
        
    except Exception as e:
        print(f"❌ Text classification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("LLM Simple Test")
    print("=" * 40)
    
    # Test text generation
    gen_success = test_text_generation()
    
    # Test text classification
    class_success = test_text_classification()
    
    # Summary
    print("\n" + "=" * 40)
    print("Test Summary:")
    print("=" * 40)
    
    if gen_success and class_success:
        print("🎉 All tests passed! LLM functionality is working correctly.")
        print("\nYou can now:")
        print("1. Use the LLM package directly in your code")
        print("2. Start the MCP Server for API access")
        print("3. Run the full example script")
    else:
        print("❌ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()