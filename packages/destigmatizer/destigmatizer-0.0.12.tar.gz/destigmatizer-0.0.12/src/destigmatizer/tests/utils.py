"""Common utilities for tests."""

import os
import sys
import argparse
from typing import Optional, Tuple, Any

from destigmatizer.utils import load_api_key, get_default_model, get_api_key_with_fallbacks


def get_api_key_for_testing(api_key: Optional[str] = None, client_type: str = "openai") -> str:
    """
    Get API key for testing from parameter, environment variables, or secrets file.
    
    Args:
        api_key: API key provided by parameter
        client_type: Type of client ("openai", "together", or "claude")
        
    Returns:
        str: API key
        
    Raises:
        SystemExit: If no API key is found
    """
    try:
        api_key, _ = get_api_key_with_fallbacks(api_key, client_type)
        return api_key
    except ValueError as e:
        print(f"Error: {e}")
        print("Please provide an API key using --api_key or set the appropriate environment variable")
        sys.exit(1)


def get_model_for_testing(model: Optional[str] = None, client_type: str = "openai") -> str:
    """
    Get model name for testing, using default if not specified.
    
    Args:
        model: Model name provided by parameter
        client_type: Type of client ("openai", "together", or "claude")
        
    Returns:
        str: Model name
    """
    if model:
        return model
    return get_default_model(client_type)


def setup_test_argument_parser(description: str) -> argparse.ArgumentParser:
    """
    Set up argument parser for test scripts.
    
    Args:
        description: Description for the argument parser
        
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--api_key', help='API key for LLM service')
    parser.add_argument('--model', help='Model name to use for testing')
    parser.add_argument('--client_type', default='together', 
                        help='Client type (e.g., openai, together, claude)')
    return parser


def parse_test_args(parser: argparse.ArgumentParser) -> Tuple[str, str, str]:
    """
    Parse common test arguments and get API key, model, and client type.
    
    Args:
        parser: Configured argument parser
        
    Returns:
        tuple: (api_key, model, client_type)
    """
    args = parser.parse_args()
    api_key = get_api_key_for_testing(args.api_key, args.client_type)
    model = get_model_for_testing(args.model, args.client_type)
    return api_key, model, args.client_type
