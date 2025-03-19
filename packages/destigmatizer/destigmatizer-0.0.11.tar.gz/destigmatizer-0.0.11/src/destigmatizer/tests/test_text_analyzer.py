import sys
import os
import json
import argparse
import destigmatizer

from destigmatizer.tests.utils import setup_test_argument_parser, parse_test_args

def test_text_analyzer(api_key=None, model=None, client_type=None):
    """
    Test the text style analysis functionality.
    
    Args:
        api_key (str, optional): API key for the LLM service
        model (str, optional): Model name to use for testing
        client_type (str, optional): Type of client ("openai", "together", "claude", etc.)
    """
    # Initialize client
    try:
        client = destigmatizer.initialize(api_key=api_key, client_type=client_type)
        print("✓ Client initialization successful")
    except Exception as e:
        print(f"Error initializing client: {e}")
        return
    
    # Test texts for analysis
    test_texts = {
        "simple_text": "This is a test sentence. It contains multiple parts.",
        "complex_text": "The complexity of language analysis cannot be overstated; various factors contribute to the nuanced understanding of written communication. For instance, sentence length, vocabulary diversity, and punctuation usage all play crucial roles in determining text style.",
        "mixed_text": "I hate this! Why can't people understand? It's not that complicated, is it? Sometimes I wonder if I'm the problem."
    }
    
    # Print model information
    print(f"Using model: {model or 'default'} with client type: {client_type}")
    
    # Test text analysis
    print("\nTesting text analysis...")
    for text_type, text in test_texts.items():
        print(f"\nAnalyzing: {text_type}")
        print(f"Text: {text}")
        result = destigmatizer.analyze_text_llm(
            text,
            client,
            model=model
        )
        print(f"Style analysis result: {result}")

if __name__ == "__main__":
    # Set up argument parser
    parser = setup_test_argument_parser('Test text style analysis functionality')
    
    # Parse arguments and get API key, model, and client type
    api_key, model, client_type = parse_test_args(parser)
    
    # Run the test
    test_text_analyzer(api_key=api_key, model=model, client_type=client_type)
