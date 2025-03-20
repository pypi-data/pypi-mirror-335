"""
Utility script for managing reframe configurations.
"""

import os
import json
import argparse
from typing import Dict, Any, Optional


def create_default_config(output_path: str, overwrite: bool = False) -> bool:
    """
    Create a default configuration file.
    
    Args:
        output_path: Path where to create the config file
        overwrite: Whether to overwrite existing file
        
    Returns:
        bool: True if successful, False otherwise
    """
    if os.path.exists(output_path) and not overwrite:
        print(f"Configuration file already exists at {output_path}.")
        print("Use --overwrite to replace it.")
        return False
        
    default_config = {
        "default_config_name": "medium_quality",
        "model_mappings": {
            "small": {
                "openai": "gpt-4o-mini",
                "together": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                "claude": "claude-3-haiku-20241022",
                "ollama": "llama3:8b",
                "gemini": "gemini-1.0-pro-001"
            },
            "medium": {
                "openai": "gpt-4o",
                "together": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                "claude": "claude-3-5-sonnet-20240620",
                "ollama": "llama3:70b",
                "gemini": "gemini-1.5-pro-001"
            },
            "large": {
                "openai": "gpt-4o-2024-05-13",
                "together": "mistralai/Mixtral-8x22B-Instruct-v0.1",
                "claude": "claude-3-opus-20240229",
                "ollama": "mixtral",
                "gemini": "gemini-1.5-flash-001"
            }
        },
        "default_models": {
            "openai": "gpt-4o",
            "together": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "claude": "claude-3-5-haiku-20241022",
            "ollama": "llama3:8b",
            "gemini": "gemini-1.0-pro-001"
        },
        "named_configs": {
            "high_quality": {
                "model_name": "large",
                "temperature": 0.0,
                "max_tokens": 4000,
                "top_p": 1.0
            },
            "medium_quality": {
                "model_name": "medium",
                "temperature": 0.0,
                "max_tokens": 2000,
                "top_p": 1.0
            },
            "low_quality": {
                "model_name": "small",
                "temperature": 0.0,
                "max_tokens": 1000,
                "top_p": 1.0
            },
            "creative": {
                "model_name": "medium",
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 0.9
            }
        }
    }
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(default_config, f, indent=2)
            
        print(f"Default configuration created at {output_path}")
        return True
    except Exception as e:
        print(f"Error creating configuration: {e}")
        return False


def load_config(config_path: str) -> Optional[Dict[str, Any]]:
    """
    Load a configuration file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        dict: Configuration data
    """
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Configuration file not found at {config_path}")
        return None
    except json.JSONDecodeError:
        print(f"Invalid JSON in configuration file {config_path}")
        return None


def add_model_mapping(config: Dict[str, Any], 
                     generic_name: str, 
                     client_type: str, 
                     model_name: str) -> Dict[str, Any]:
    """
    Add or update a model mapping.
    
    Args:
        config: Configuration dictionary
        generic_name: Generic model name (e.g., "small", "medium", "large")
        client_type: Client type (e.g., "openai", "claude")
        model_name: Actual model name
        
    Returns:
        dict: Updated configuration
    """
    if "model_mappings" not in config:
        config["model_mappings"] = {}
        
    if generic_name not in config["model_mappings"]:
        config["model_mappings"][generic_name] = {}
        
    config["model_mappings"][generic_name][client_type] = model_name
    return config


def add_named_config(config: Dict[str, Any],
                    name: str,
                    model_name: str,
                    temperature: float = 0.0,
                    max_tokens: int = 2000,
                    top_p: float = 1.0,
                    **kwargs) -> Dict[str, Any]:
    """
    Add or update a named configuration.
    
    Args:
        config: Configuration dictionary
        name: Name for this configuration
        model_name: Model name or generic name
        temperature: Temperature parameter
        max_tokens: Maximum tokens
        top_p: Top-p sampling parameter
        **kwargs: Additional parameters
        
    Returns:
        dict: Updated configuration
    """
    if "named_configs" not in config:
        config["named_configs"] = {}
        
    named_config = {
        "model_name": model_name,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p
    }
    
    # Add any additional parameters
    named_config.update(kwargs)
    
    config["named_configs"][name] = named_config
    return config


def set_default_model(config: Dict[str, Any], 
                     client_type: str, 
                     model_name: str) -> Dict[str, Any]:
    """
    Set the default model for a client type.
    
    Args:
        config: Configuration dictionary
        client_type: Client type
        model_name: Model name
        
    Returns:
        dict: Updated configuration
    """
    if "default_models" not in config:
        config["default_models"] = {}
        
    config["default_models"][client_type] = model_name
    return config


def save_config(config: Dict[str, Any], output_path: str) -> bool:
    """
    Save configuration to file.
    
    Args:
        config: Configuration dictionary
        output_path: Path to save the file
        
    Returns:
        bool: True if successful
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        print(f"Configuration saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False


def get_user_config_path() -> str:
    """
    Get the recommended path for the user configuration file.
    
    Returns:
        str: Path to the user configuration file
    """
    home_dir = os.path.expanduser("~")
    config_dir = os.path.join(home_dir, ".reframe")
    return os.path.join(config_dir, "config.json")

def get_effective_config() -> Dict[str, Any]:
    """
    Get the effective configuration by checking all standard locations.
    
    Returns:
        dict: The effective configuration
    """
    # Import the function from utils to avoid circular imports
    # We need to do dynamic import since this file might be run directly
    try:
        # Try to import from the installed package
        from destigmatizer.utils import load_user_model_configs
        return load_user_model_configs() or {}
    except ImportError:
        # If running directly, try relative import
        try:
            import sys
            import os.path
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from utils import load_user_model_configs
            return load_user_model_configs() or {}
        except ImportError:
            print("Warning: Could not import utils module. Checking standard locations directly.")
            
            # Fallback implementation if we can't import the function
            module_dir = os.path.dirname(os.path.abspath(__file__))
            package_dir = os.path.dirname(module_dir)
            
            locations = [
                os.path.join(module_dir, "config", "reframe_config.json"),
                os.path.join(package_dir, "config", "reframe_config.json"),
                os.path.join(os.getcwd(), "reframe_config.json"),
                os.path.join(os.getcwd(), "config", "reframe_config.json"),
                os.path.join(os.path.expanduser("~"), ".reframe", "config.json"),
                os.environ.get("REFRAME_CONFIG_PATH")
            ]
            
            for location in locations:
                if location and os.path.exists(location):
                    try:
                        with open(location, 'r') as f:
                            return json.load(f)
                    except json.JSONDecodeError:
                        continue
                        
            return {}

def display_config(config: Dict[str, Any], indent: int = 0) -> None:
    """
    Display the configuration in a readable format.
    
    Args:
        config: Configuration dictionary
        indent: Current indentation level
    """
    indent_str = "  " * indent
    
    for key, value in config.items():
        if isinstance(value, dict):
            print(f"{indent_str}{key}:")
            display_config(value, indent + 1)
        else:
            print(f"{indent_str}{key}: {value}")

def main():
    parser = argparse.ArgumentParser(description="Reframe Configuration Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create default config command
    create_parser = subparsers.add_parser("create", help="Create default configuration file")
    create_parser.add_argument("--output", "-o", default="./reframe_config.json", 
                             help="Output path for the configuration file")
    create_parser.add_argument("--overwrite", action="store_true", 
                             help="Overwrite existing configuration file")
    
    # Add model mapping command
    map_parser = subparsers.add_parser("map", help="Add or update a model mapping")
    map_parser.add_argument("--config", "-c", required=True, 
                          help="Path to the configuration file")
    map_parser.add_argument("--generic", "-g", required=True, 
                          help="Generic model name (small, medium, large, etc.)")
    map_parser.add_argument("--client", "-l", required=True, 
                          help="Client type (openai, claude, etc.)")
    map_parser.add_argument("--model", "-m", required=True, 
                          help="Actual model name")
    
    # Add named config command
    named_parser = subparsers.add_parser("add", help="Add or update a named configuration")
    named_parser.add_argument("--config", "-c", required=True, 
                            help="Path to the configuration file")
    named_parser.add_argument("--name", "-n", required=True, 
                            help="Name for this configuration")
    named_parser.add_argument("--model", "-m", required=True, 
                            help="Model name or generic name")
    named_parser.add_argument("--temperature", "-t", type=float, default=0.0, 
                            help="Temperature parameter")
    named_parser.add_argument("--max-tokens", type=int, default=2000, 
                            help="Maximum tokens")
    named_parser.add_argument("--top-p", type=float, default=1.0, 
                            help="Top-p sampling parameter")
    
    # Set default model command
    default_parser = subparsers.add_parser("default", help="Set default model for client type")
    default_parser.add_argument("--config", "-c", required=True, 
                              help="Path to the configuration file")
    default_parser.add_argument("--client", "-l", required=True, 
                              help="Client type (openai, claude, etc.)")
    default_parser.add_argument("--model", "-m", required=True, 
                              help="Model name")
    
    # Initialize user config in recommended location
    init_parser = subparsers.add_parser("init", help="Initialize user config in recommended location")
    init_parser.add_argument("--overwrite", action="store_true", 
                           help="Overwrite existing configuration file")
                           
    # Show current effective configuration
    show_parser = subparsers.add_parser("show", help="Show current effective configuration")
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == "create":
        create_default_config(args.output, args.overwrite)
    
    elif args.command == "map":
        config = load_config(args.config)
        if config:
            config = add_model_mapping(config, args.generic, args.client, args.model)
            save_config(config, args.config)
    
    elif args.command == "add":
        config = load_config(args.config)
        if config:
            config = add_named_config(config, args.name, args.model, 
                                     args.temperature, args.max_tokens, args.top_p)
            save_config(config, args.config)
    
    elif args.command == "default":
        config = load_config(args.config)
        if config:
            config = set_default_model(config, args.client, args.model)
            save_config(config, args.config)
    
    elif args.command == "init":
        # Initialize user config in recommended location
        user_config_path = get_user_config_path()
        create_default_config(user_config_path, args.overwrite)
    
    elif args.command == "show":
        # Show current effective configuration
        config = get_effective_config()
        if config:
            print("Current effective configuration:")
            display_config(config)
        else:
            print("No configuration found. Run 'reframe config init' to create a default configuration.")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
