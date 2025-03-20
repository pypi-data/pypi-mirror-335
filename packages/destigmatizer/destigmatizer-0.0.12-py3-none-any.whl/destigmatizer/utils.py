"""Utility functions for the reframe package."""

import os
import json
import time
from typing import Dict, Any, Optional, Tuple, Union


def load_api_key(client_type: str) -> Optional[str]:
    """
    Load API key from environment variables or secrets file.
    
    Args:
        client_type: Type of client ("openai", "together", or "claude")
        
    Returns:
        str: API key if found, None otherwise
    """
    env_var_name = None
    secret_key_name = None
    
    if client_type.lower() == "openai":
        env_var_name = "OPENAI_API_KEY"
        secret_key_name = "OPENAI_API_KEY"
    elif client_type.lower() == "together":
        env_var_name = "TOGETHER_API_KEY"
        secret_key_name = "TOGETHER_API_KEY"
    elif client_type.lower() == "claude":
        env_var_name = "ANTHROPIC_API_KEY"
        secret_key_name = "ANTHROPIC_API_KEY"
    else:
        return None
    
    # Try environment variable first
    api_key = os.environ.get(env_var_name)
    if api_key:
        return api_key
    
    # Try secrets.json file
    try:
        with open("secrets.json") as f:
            secrets = json.load(f)
            return secrets.get(secret_key_name)
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None

def get_model_mapping(model_name: Optional[str] = None, client_type: str = "openai") -> str:
    """
    Map generic model names to provider-specific model names.
    
    Args:
        model_name: Generic model name like "small", "medium", "large"
        client_type: Type of client ("openai", "together", "claude")
        
    Returns:
        str: Provider-specific model name
    """
    # Try to load user config first
    user_config = load_user_model_configs()
    model_mappings = user_config.get("model_mappings", {})
    
    # If no config or missing mappings, use defaults
    if not model_mappings:
        model_mappings = {
            "small": {
                "openai": "gpt-4o-mini",
                "together": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                "claude": "claude-3-haiku-20241022",
            },
            "medium": {
                "openai": "gpt-4o",
                "together": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                "claude": "claude-3-5-sonnet-20240620",
            },
            "large": {
                "openai": "gpt-4o-2024-05-13",
                "together": "mistralai/Mixtral-8x22B-Instruct-v0.1",
                "claude": "claude-3-opus-20240229",
            }
        }
    
    # If a generic name is provided, map it
    if model_name in model_mappings:
        return model_mappings[model_name].get(client_type, get_default_model(client_type))
    
    # If a specific model name is provided, use it directly
    if model_name:
        return model_name
    
    # Otherwise return the default for the client type
    return get_default_model(client_type)

def get_default_model(client_type: str) -> Optional[str]:
    """
    Get the default model for a given client type.
    
    Args:
        client_type: Type of client ("openai", "together", "claude", or other providers)
        
    Returns:
        str: Default model name for the client type, None if client type is unsupported
    """
    # Try to load user config first
    user_config = load_user_model_configs()
    default_models = user_config.get("default_models", {})
    
    # If config has this client type, use that model
    if client_type.lower() in default_models:
        return default_models[client_type.lower()]
    
    # Otherwise fall back to hardcoded defaults
    client_defaults = {
        "openai": "gpt-4o",
        "together": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "claude": "claude-3-5-haiku-20241022",
        "ollama": "llama3:8b", 
        "gemini": "gemini-1.0-pro-001"
    }
    
    return client_defaults.get(client_type.lower())


def determine_client_type() -> Optional[str]:
    """
    Determine client type based on available API keys.
    
    Returns:
        str: Detected client type, None if no API keys are found
    """
    # Check environment variables first
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    elif os.environ.get("TOGETHER_API_KEY"):
        return "together"
    elif os.environ.get("ANTHROPIC_API_KEY"):
        return "claude"
    
    # Check secrets.json file
    try:
        with open("secrets.json") as f:
            secrets = json.load(f)
            if secrets.get("OPENAI_API_KEY"):
                return "openai"
            elif secrets.get("TOGETHER_API_KEY"):
                return "together"
            elif secrets.get("ANTHROPIC_API_KEY"):
                return "claude"
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    return None


def retry_with_backoff(func, max_retries: int = 3, initial_wait: float = 1.0, 
                      backoff_factor: float = 2.0, **kwargs):
    """
    Execute a function with exponential backoff retry logic.
    
    Args:
        func: Function to execute
        max_retries: Maximum number of retries
        initial_wait: Initial wait time in seconds
        backoff_factor: Factor to multiply wait time by after each retry
        **kwargs: Arguments to pass to func
        
    Returns:
        Any: Result of func if successful
        
    Raises:
        Exception: Last exception encountered if all retries fail
    """
    wait_time = initial_wait
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return func(**kwargs)
        except Exception as e:
            last_exception = e
            if attempt == max_retries:
                break
                
            print(f"Attempt {attempt + 1} failed: {e}, retrying in {wait_time:.1f}s...")
            time.sleep(wait_time)
            wait_time *= backoff_factor
    
    raise last_exception


def get_api_key_with_fallbacks(api_key: Optional[str] = None, client_type: Optional[str] = None) -> Tuple[str, str]:
    """
    Get API key with fallbacks to environment variables and secrets file.
    Also determines client type if not specified.
    
    Args:
        api_key: API key provided directly (highest priority)
        client_type: Type of client, will be determined if None
        
    Returns:
        tuple: (api_key, client_type)
        
    Raises:
        ValueError: If no API key can be found
    """
    # If API key provided directly, use it
    if api_key:
        # If client_type not provided, try to determine based on API key format/prefixes
        if client_type is None:
            if api_key.startswith(("sk-ant", "sk-a")):
                client_type = "claude"
            elif api_key.startswith("sk-"):
                client_type = "openai"
            else:
                client_type = "together"  # Fallback to Together if we can't determine
        return api_key, client_type
    
    # If client_type provided but no API key, try to find key for that type
    if client_type:
        api_key = load_api_key(client_type)
        if api_key:
            return api_key, client_type
    
    # Try to determine client type from available keys
    client_type = determine_client_type()
    if client_type:
        api_key = load_api_key(client_type)
        if api_key:
            return api_key, client_type
    
    raise ValueError("No API key found. Please provide an API key or set the appropriate environment variable.")


def identify_client(client: Any) -> str:
    """
    Identify the type of client from an instance.
    
    Args:
        client: Client instance
        
    Returns:
        str: Client type ("openai", "together", "claude", or "unknown")
    """
    if hasattr(client, "client_type"):
        return client.client_type
    
    # Check by class name
    client_class_name = client.__class__.__name__.lower()
    if "openai" in client_class_name:
        return "openai"
    elif "together" in client_class_name:
        return "together"
    elif "anthropic" in client_class_name or "claude" in client_class_name:
        return "claude"
    
    # Check by attributes/methods
    if hasattr(client, "chat") and hasattr(client.chat, "completions"):
        return "openai"  # OpenAI-compatible API
    elif hasattr(client, "messages") and hasattr(client.messages, "create"):
        return "claude"
    
    return "unknown"

def load_user_model_configs() -> Dict[str, Any]:
    """
    Load user configuration from standard locations.
    
    Checks multiple locations in this order:
    1. Environment variable REFRAME_CONFIG_PATH
    2. User's home directory ~/.reframe/config.json
    3. Current working directory reframe_config.json or config/reframe_config.json
    4. Package directory
    
    Returns:
        dict: Configuration dictionary, empty dict if no config found
    """
    # Standard locations to check
    locations = [
        os.environ.get("REFRAME_CONFIG_PATH"),
        os.path.join(os.path.expanduser("~"), ".reframe", "config.json"),
        os.path.join(os.getcwd(), "reframe_config.json"),
        os.path.join(os.getcwd(), "config", "reframe_config.json"),
    ]
    
    # Also check in package directory
    try:
        module_dir = os.path.dirname(os.path.abspath(__file__))
        package_dir = os.path.dirname(module_dir)
        
        locations.extend([
            os.path.join(module_dir, "config", "reframe_config.json"),
            os.path.join(package_dir, "config", "reframe_config.json"),
        ])
    except Exception:
        pass
    
    # Try each location
    for location in locations:
        if location and os.path.exists(location):
            try:
                with open(location, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, PermissionError):
                continue
    
    return {}