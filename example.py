#!/usr/bin/env python3
"""
Example script demonstrating LLM and MCP Server usage.

This script shows how to:
1. Use the LLM package for text generation and classification
2. Start the MCP Server
3. Make API calls to the server
"""

import asyncio
import requests
import time
import json
from typing import Dict, Any

# Import LLM components
from llm.models.transformer_model import TransformerModel
from llm.models.text_classifier import TextClassifier
from llm.models.text_generator import TextGenerator

def demo_llm_usage():
    """Demonstrate direct LLM usage."""
    print("=" * 50)
    print("LLM Package Demo")
    print("=" * 50)
    
    try:
        # Initialize text generator
        print("Initializing text generator...")
        generator = TextGenerator("gpt2")
        
        # Generate text
        prompt = "The future of artificial intelligence is"
        print(f"\nGenerating text for prompt: '{prompt}'")
        generated_text = generator.generate(
            prompt=prompt,
            max_length=100,
            temperature=0.8
        )
        print(f"Generated: {generated_text}")
        
        # Generate story
        print("\nGenerating a story...")
        story = generator.generate_story(
            title="The AI Adventure",
            genre="science fiction",
            max_length=200
        )
        print(f"Story: {story}")
        
        # Initialize text classifier
        print("\nInitializing text classifier...")
        classifier = TextClassifier("distilbert-base-uncased-finetuned-sst-2-english")
        
        # Classify text
        texts = [
            "I love this movie! It's amazing!",
            "This is the worst film I've ever seen.",
            "The weather is nice today."
        ]
        
        print("\nClassifying texts:")
        for text in texts:
            result = classifier.classify(text)
            print(f"Text: {text}")
            print(f"Classification: {result}")
            print()
        
        # Get model information
        print("Model Information:")
        gen_info = generator.get_model_info()
        class_info = classifier.get_model_info()
        
        print(f"Generator - Parameters: {gen_info['num_parameters']:,}")
        print(f"Classifier - Parameters: {class_info['num_parameters']:,}")
        
    except Exception as e:
        print(f"Error in LLM demo: {str(e)}")

def demo_mcp_server_api():
    """Demonstrate MCP Server API usage."""
    print("\n" + "=" * 50)
    print("MCP Server API Demo")
    print("=" * 50)
    
    # Server configuration
    base_url = "http://localhost:8000"
    api_base = f"{base_url}/api/v1"
    
    try:
        # Check server health
        print("Checking server health...")
        health_response = requests.get(f"{base_url}/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"Server status: {health_data['status']}")
            print(f"Uptime: {health_data['uptime']:.2f} seconds")
        else:
            print(f"Server health check failed: {health_response.status_code}")
            return
        
        # Text generation via API
        print("\nGenerating text via API...")
        gen_data = {
            "prompt": "The future of artificial intelligence is",
            "max_length": 100,
            "temperature": 0.8
        }
        
        gen_response = requests.post(f"{api_base}/inference/generate", json=gen_data)
        if gen_response.status_code == 200:
            gen_result = gen_response.json()
            print(f"Generated text: {gen_result['result']}")
            print(f"Processing time: {gen_result['processing_time_ms']}ms")
        else:
            print(f"Text generation failed: {gen_response.status_code}")
        
        # Text classification via API
        print("\nClassifying text via API...")
        class_data = {
            "text": "I love this movie! It's amazing!",
            "return_probabilities": True
        }
        
        class_response = requests.post(f"{api_base}/inference/classify", json=class_data)
        if class_response.status_code == 200:
            class_result = class_response.json()
            print(f"Classification result: {class_result['result']}")
            print(f"Processing time: {class_result['processing_time_ms']}ms")
        else:
            print(f"Text classification failed: {class_response.status_code}")
        
        # Get available models
        print("\nGetting available models...")
        models_response = requests.get(f"{api_base}/inference/models")
        if models_response.status_code == 200:
            models_data = models_response.json()
            print(f"Available models: {models_data['total']}")
            for model in models_data['models']:
                print(f"  - {model['model_id']} ({model['task_type']})")
        else:
            print(f"Failed to get models: {models_response.status_code}")
        
        # Get inference statistics
        print("\nGetting inference statistics...")
        stats_response = requests.get(f"{api_base}/inference/stats")
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print(f"Statistics: {stats_data}")
        else:
            print(f"Failed to get statistics: {stats_response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print("Could not connect to MCP Server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"Error in MCP Server API demo: {str(e)}")

async def demo_async_inference():
    """Demonstrate async inference capabilities."""
    print("\n" + "=" * 50)
    print("Async Inference Demo")
    print("=" * 50)
    
    try:
        # This would require the MCP Server to be running
        # For now, we'll just show the concept
        print("Async inference would be used for:")
        print("- Batch processing multiple requests")
        print("- Real-time streaming responses")
        print("- Concurrent model inference")
        print("- WebSocket-based communication")
        
    except Exception as e:
        print(f"Error in async inference demo: {str(e)}")

def main():
    """Main function to run all demos."""
    print("LLM and MCP Server Demo")
    print("This script demonstrates the capabilities of both the LLM package and MCP Server")
    print()
    
    # Demo 1: Direct LLM usage
    demo_llm_usage()
    
    # Demo 2: MCP Server API usage
    demo_mcp_server_api()
    
    # Demo 3: Async inference
    asyncio.run(demo_async_inference())
    
    print("\n" + "=" * 50)
    print("Demo Complete!")
    print("=" * 50)
    print("\nTo start the MCP Server, run:")
    print("python main.py")
    print("\nOr with uvicorn:")
    print("uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    print("\nThen visit http://localhost:8000/docs for the interactive API documentation")

if __name__ == "__main__":
    main()