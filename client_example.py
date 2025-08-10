#!/usr/bin/env python3
"""
Client example script demonstrating how to use the LLM API.
"""

import requests
import json
import time

# Server configuration
BASE_URL = "http://localhost:8001"

def test_server_health():
    """Test if the server is healthy."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is healthy!")
            print(f"Models loaded: {data['models_loaded']}")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Could not connect to server: {e}")
        return False

def generate_text(prompt, max_length=50, temperature=0.7):
    """Generate text using the API."""
    try:
        data = {
            "prompt": prompt,
            "max_length": max_length,
            "temperature": temperature
        }
        
        response = requests.post(f"{BASE_URL}/generate", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Text generation successful!")
            print(f"Generated text: {result['generated_text']}")
            print(f"Processing time: {result['processing_time_ms']}ms")
            print(f"Model used: {result['model_used']}")
            return result
        else:
            print(f"❌ Text generation failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error in text generation: {e}")
        return None

def classify_text(text):
    """Classify text using the API."""
    try:
        data = {"text": text}
        
        response = requests.post(f"{BASE_URL}/classify", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Text classification successful!")
            print(f"Text: {text}")
            print(f"Classification: {result['classification']['label']}")
            print(f"Confidence: {result['classification']['score']:.4f}")
            print(f"Processing time: {result['processing_time_ms']}ms")
            print(f"Model used: {result['model_used']}")
            return result
        else:
            print(f"❌ Text classification failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error in text classification: {e}")
        return None

def get_models_info():
    """Get information about available models."""
    try:
        response = requests.get(f"{BASE_URL}/models")
        
        if response.status_code == 200:
            models = response.json()
            print("✅ Models information:")
            for model_type, info in models.items():
                status = "✅ Loaded" if info['loaded'] else "❌ Not loaded"
                print(f"  {model_type}: {info['model_name']} ({status})")
            return models
        else:
            print(f"❌ Failed to get models info: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting models info: {e}")
        return None

def interactive_demo():
    """Run an interactive demo."""
    print("\n" + "="*50)
    print("Interactive LLM API Demo")
    print("="*50)
    
    while True:
        print("\nOptions:")
        print("1. Generate text")
        print("2. Classify text")
        print("3. Show models info")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            prompt = input("Enter your prompt: ").strip()
            if prompt:
                max_length = input("Enter max length (default 50): ").strip()
                max_length = int(max_length) if max_length.isdigit() else 50
                
                temperature = input("Enter temperature (default 0.7): ").strip()
                temperature = float(temperature) if temperature.replace('.', '').isdigit() else 0.7
                
                generate_text(prompt, max_length, temperature)
        
        elif choice == "2":
            text = input("Enter text to classify: ").strip()
            if text:
                classify_text(text)
        
        elif choice == "3":
            get_models_info()
        
        elif choice == "4":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

def main():
    """Main function."""
    print("LLM API Client Example")
    print("="*40)
    
    # Test server health
    if not test_server_health():
        print("❌ Server is not available. Please start the server first.")
        print("Run: python simple_server.py")
        return
    
    # Get models info
    get_models_info()
    
    # Demo examples
    print("\n" + "="*40)
    print("Demo Examples")
    print("="*40)
    
    # Text generation examples
    print("\n1. Text Generation Examples:")
    generate_text("The future of artificial intelligence is", max_length=100, temperature=0.8)
    generate_text("Once upon a time in a magical forest", max_length=80, temperature=0.9)
    
    # Text classification examples
    print("\n2. Text Classification Examples:")
    classify_text("I love this movie! It's absolutely fantastic!")
    classify_text("This product is terrible and doesn't work at all.")
    classify_text("The weather is nice today.")
    
    # Interactive demo
    print("\n" + "="*40)
    print("Interactive Demo")
    print("="*40)
    print("You can now try the API interactively!")
    
    try:
        interactive_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye!")

if __name__ == "__main__":
    main()