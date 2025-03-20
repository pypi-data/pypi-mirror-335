"""Client abstractions for different LLM providers."""

import os
import json
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @property
    @abstractmethod
    def client_type(self) -> str:
        """Return the type of this client."""
        pass
    
    @abstractmethod
    def create_completion(self, 
                         messages: List[Dict[str, str]], 
                         model: Optional[str] = None, 
                         temperature: float = 0, 
                         max_tokens: int = 1000) -> str:
        """Generate a completion from the LLM.
        
        Args:
            messages: List of message dictionaries
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            str: The generated response content
        """
        pass
    
    @classmethod
    def from_env(cls, api_key: Optional[str] = None) -> 'LLMClient':
        """Create a client instance using environment variables or provided API key."""
        pass


class OpenAIClient(LLMClient):
    """Client for OpenAI API."""
    
    def __init__(self, api_key: str):
        """Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key
        """
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
    
    @property
    def client_type(self) -> str:
        """Return the type of this client."""
        return "openai"
        
    def create_completion(self, 
                         messages: List[Dict[str, str]], 
                         model: Optional[str] = None, 
                         temperature: float = 0, 
                         max_tokens: int = 1000) -> str:
        """Generate a completion from OpenAI.
        
        Args:
            messages: List of message dictionaries
            model: OpenAI model to use
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            str: The generated response content
        """
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error creating completion with OpenAI: {str(e)}")
    
    @classmethod
    def from_env(cls, api_key: Optional[str] = None) -> 'OpenAIClient':
        """Create an OpenAI client instance using environment variables or provided API key."""
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key is None:
                try:
                    with open("secrets.json") as f:
                        secrets = json.load(f)
                        api_key = secrets.get("OPENAI_API_KEY")
                except (FileNotFoundError, json.JSONDecodeError, KeyError):
                    pass
                    
        if api_key is None:
            raise ValueError("No OpenAI API key found in environment or secrets file")
            
        return cls(api_key)


class TogetherClient(LLMClient):
    """Client for Together API."""
    
    def __init__(self, api_key: str):
        """Initialize Together client.
        
        Args:
            api_key: Together API key
        """
        from together import Together
        self.client = Together(api_key=api_key)
    
    @property
    def client_type(self) -> str:
        """Return the type of this client."""
        return "together"
        
    def create_completion(self, 
                         messages: List[Dict[str, str]], 
                         model: Optional[str] = None, 
                         temperature: float = 0, 
                         max_tokens: int = 1000) -> str:
        """Generate a completion from Together.
        
        Args:
            messages: List of message dictionaries
            model: Together model to use
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            str: The generated response content
        """
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error creating completion with Together: {str(e)}")
    
    @classmethod
    def from_env(cls, api_key: Optional[str] = None) -> 'TogetherClient':
        """Create a Together client instance using environment variables or provided API key."""
        if api_key is None:
            api_key = os.environ.get("TOGETHER_API_KEY")
            if api_key is None:
                try:
                    with open("secrets.json") as f:
                        secrets = json.load(f)
                        api_key = secrets.get("TOGETHER_API_KEY")
                except (FileNotFoundError, json.JSONDecodeError, KeyError):
                    pass
                    
        if api_key is None:
            raise ValueError("No Together API key found in environment or secrets file")
            
        return cls(api_key)


class ClaudeClient(LLMClient):
    """Client for Anthropic's Claude API."""
    
    def __init__(self, api_key: str):
        """Initialize Claude client.
        
        Args:
            api_key: Anthropic API key
        """
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
    
    @property
    def client_type(self) -> str:
        """Return the type of this client."""
        return "claude"
        
    def create_completion(self, 
                         messages: List[Dict[str, str]], 
                         model: Optional[str] = None, 
                         temperature: float = 0, 
                         max_tokens: int = 1000) -> str:
        """Generate a completion from Claude.
        
        Args:
            messages: List of message dictionaries
            model: Claude model to use
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            str: The generated response content
        """
        try:
            # Extract system message if present
            system_message = next((m["content"] for m in messages if m["role"] == "system"), None)
            
            # Prepare the messages for Claude API by restructuring
            claude_messages = []
            for m in messages:
                if m["role"] == "system":
                    continue  # Skip system messages as we handle them separately
                claude_messages.append({
                    "role": m["role"],
                    "content": m["content"]
                })
            
            response = self.client.messages.create(
                model=model,
                system=system_message,
                messages=claude_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Error creating completion with Claude: {str(e)}")
    
    @classmethod
    def from_env(cls, api_key: Optional[str] = None) -> 'ClaudeClient':
        """Create a Claude client instance using environment variables or provided API key."""
        if api_key is None:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if api_key is None:
                try:
                    with open("secrets.json") as f:
                        secrets = json.load(f)
                        api_key = secrets.get("ANTHROPIC_API_KEY")
                except (FileNotFoundError, json.JSONDecodeError, KeyError):
                    pass
                    
        if api_key is None:
            raise ValueError("No Anthropic API key found in environment or secrets file")
            
        return cls(api_key)


def get_client(client_type: str = None, api_key: str = None) -> LLMClient:
    """Factory function to create the appropriate client based on type.
    
    Args:
        client_type: Type of client ("openai", "together", or "claude")
        api_key: API key to use
        
    Returns:
        LLMClient: An instance of the appropriate client
    """
    if client_type is None:
        # Try to determine from environment variables
        if os.environ.get("OPENAI_API_KEY"):
            client_type = "openai"
        elif os.environ.get("TOGETHER_API_KEY"):
            client_type = "together"
        elif os.environ.get("ANTHROPIC_API_KEY"):
            client_type = "claude"
        else:
            # Check secrets.json
            try:
                with open("secrets.json") as f:
                    secrets = json.load(f)
                    if secrets.get("OPENAI_API_KEY"):
                        client_type = "openai"
                    elif secrets.get("TOGETHER_API_KEY"):
                        client_type = "together"
                    elif secrets.get("ANTHROPIC_API_KEY"):
                        client_type = "claude"
            except (FileNotFoundError, json.JSONDecodeError):
                pass
    
    if client_type is None:
        raise ValueError("Could not determine client type from environment variables or secrets")
    
    if client_type.lower() == "openai":
        return OpenAIClient.from_env(api_key)
    elif client_type.lower() == "together":
        return TogetherClient.from_env(api_key)
    elif client_type.lower() == "claude":
        return ClaudeClient.from_env(api_key)
    else:
        raise ValueError(f"Unsupported client type: {client_type}")


def detect_client_type(client: Any) -> str:
    """
    Detect client type from a client instance.
    
    Args:
        client: Client instance
        
    Returns:
        str: Detected client type ("openai", "together", "claude", or "unknown")
    """
    if isinstance(client, LLMClient):
        return client.client_type
    
    # For backward compatibility with raw clients
    client_class_name = client.__class__.__name__.lower()
    if "openai" in client_class_name:
        return "openai"
    elif "together" in client_class_name:
        return "together"
    elif "anthropic" in client_class_name or "claude" in client_class_name:
        return "claude"
    
    return "unknown"
