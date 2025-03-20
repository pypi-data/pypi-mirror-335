import sys
import os
import json
import argparse
import destigmatizer

from destigmatizer.tests.utils import setup_test_argument_parser, parse_test_args

def test_stigma_classifier(api_key=None, model=None, client_type=None):
    """
    Test the stigma classification functionality.
    
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

    # Test posts for classification
    test_posts = {
        "stigma_post_1": "All these junkies should be locked up, they're ruining our city",
        "stigma_post_2": "Once an addict, always an addict. They'll never change.",
        "non_stigma_post_1": "People struggling with addiction need support and understanding",
        "non_stigma_post_2": "My friend is in recovery from opioid use disorder and is doing incredibly well."
    }
    
    # Print model information
    print(f"Using model: {model or 'default'} with client type: {client_type}")
    
    # Test stigma classification
    print("\nTesting stigma classification...")
    for post_type, post in test_posts.items():
        print(f"\nTesting on: {post}")
        result = destigmatizer.classify_if_stigma(
            post,
            client=client,
            model=model
        )
        print(f"{post_type}: {result}")
        
        # If stigmatizing, show the explanation (which follows after the "S, " prefix)
        if result.startswith("s,"):
            print(f"Explanation: {result[2:].strip()}")

if __name__ == "__main__":
    # Set up argument parser
    parser = setup_test_argument_parser('Test stigma classification functionality')
    
    # Parse arguments and get API key, model, and client type
    api_key, model, client_type = parse_test_args(parser)
    
    # Run the test
    test_stigma_classifier(api_key=api_key, model=model, client_type=client_type)
