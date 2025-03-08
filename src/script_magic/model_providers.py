"""
Model provider abstraction for different AI services.

This module provides abstract base classes and concrete implementations for different AI model providers
(OpenAI, Anthropic, Google) with lazy loading of dependencies.
"""
from abc import ABC, abstractmethod
from typing import Optional, Any, Type
from pydantic import BaseModel
import importlib.util

class AIModelProvider(ABC):
    """Abstract base class for AI model providers."""
    
    @abstractmethod
    def is_compatible_model(self, model_name: str) -> bool:
        """Check if this provider can handle the given model name."""
        pass
    
    @abstractmethod
    def initialize_client(self, api_key: Optional[str] = None) -> Any:
        """Initialize and return the client for this provider."""
        pass
    
    @abstractmethod
    def generate_completion(self, 
                          prompt: str, 
                          model: str, 
                          response_model: Type[BaseModel],
                          **kwargs) -> Any:
        """Generate a completion using the specified model."""
        pass

class AnthropicProvider(AIModelProvider):
    """Anthropic AI model provider implementation."""
    
    def __init__(self):
        self._client = None
        self._instructor = None
    
    def is_compatible_model(self, model_name: str) -> bool:
        return model_name.startswith("claude-")
    
    def initialize_client(self, api_key: Optional[str] = None) -> Any:
        if self._client is None:
            try:
                anthropic_spec = importlib.util.find_spec("anthropic")
                instructor_spec = importlib.util.find_spec("instructor")
                
                if not anthropic_spec or not instructor_spec:
                    raise ImportError("Required packages not found. Install with: pip install anthropic instructor")
                
                import anthropic
                import instructor
                
                self._instructor = instructor
                self._client = instructor.from_anthropic(
                    anthropic.Anthropic(api_key=api_key),
                    mode=instructor.Mode.ANTHROPIC_TOOLS
                )
            except ImportError as e:
                raise ImportError(f"Failed to initialize Anthropic client: {str(e)}")
        return self._client
    
    def generate_completion(self, 
                          prompt: str, 
                          model: str, 
                          response_model: Type[BaseModel],
                          **kwargs) -> Any:
        client = self.initialize_client()
        
        # Create the messages array with system and user roles
        messages = []
        if "system_message" in kwargs:
            messages.append({"role": "system", "content": kwargs.pop("system_message")})
        messages.append({"role": "user", "content": prompt})

        # Pass through any additional kwargs like max_tokens, temperature, etc.
        return client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=8192,
            response_model=response_model,
            **kwargs
        )

class OpenAIProvider(AIModelProvider):
    """OpenAI model provider implementation."""
    
    MODEL_MAPPING = {
        "gpt-4o-mini": "gpt-4",  # Map our custom name to actual OpenAI model name
    }
    
    def __init__(self):
        self._client = None
        self._instructor = None
    
    def is_compatible_model(self, model_name: str) -> bool:
        return model_name.startswith(("gpt-", "o1-", "o3-")) or model_name in self.MODEL_MAPPING
    
    def initialize_client(self, api_key: Optional[str] = None) -> Any:
        if self._client is None:
            try:
                openai_spec = importlib.util.find_spec("openai")
                instructor_spec = importlib.util.find_spec("instructor")
                
                if not openai_spec or not instructor_spec:
                    raise ImportError("Required packages not found. Install with: pip install openai instructor")
                
                from openai import OpenAI
                import instructor
                
                self._instructor = instructor
                self._client = instructor.from_openai(
                    OpenAI(api_key=api_key)
                )
            except ImportError as e:
                raise ImportError(f"Failed to initialize OpenAI client: {str(e)}")
        return self._client
    
    def generate_completion(self, 
                          prompt: str, 
                          model: str, 
                          response_model: Type[BaseModel],
                          **kwargs) -> Any:
        client = self.initialize_client()
        return client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_model=response_model,
            **kwargs
        )

class GoogleProvider(AIModelProvider):
    """Google AI model provider implementation."""
    
    def __init__(self):
        self._client = None
        self._instructor = None
        self._model = None
    
    def is_compatible_model(self, model_name: str) -> bool:
        return model_name.startswith("gemini-")
    
    def initialize_client(self, api_key: Optional[str] = None) -> Any:
        if self._client is None:
            try:
                genai_spec = importlib.util.find_spec("google.generativeai")
                instructor_spec = importlib.util.find_spec("instructor")
                
                if not genai_spec or not instructor_spec:
                    raise ImportError("Required packages not found. Install with: pip install google-generativeai instructor jsonref")
                
                import google.generativeai as genai
                import instructor
                
                self._instructor = instructor
                if api_key:
                    genai.configure(api_key=api_key)
                
                # Store model for later use
                self._model = "gemini-1.5-flash-latest"
                    
                self._client = instructor.from_gemini(
                    client=genai.GenerativeModel(
                        model_name=self._model
                    ),
                    mode=instructor.Mode.GEMINI_JSON
                )
            except ImportError as e:
                raise ImportError(f"Failed to initialize Google AI client: {str(e)}")
        return self._client
    
    def generate_completion(self, 
                          prompt: str, 
                          model: str, 
                          response_model: Type[BaseModel],
                          **kwargs) -> Any:
        client = self.initialize_client()
        # Note: We ignore the model parameter as it's set during client initialization
        return client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            response_model=response_model,
            **kwargs
        )

class ModelManager:
    """Manager class to handle different AI model providers."""
    
    DEFAULT_MODELS = {
        "default": "claude-3-7-sonnet-20250219",
        "fast": "gpt-4o-mini",
        "powerful": "claude-3-7-sonnet-20250219",
        "balanced": "gemini-2.0-flash-20250227",
    }
    
    def __init__(self):
        self.providers = [
            AnthropicProvider(),
            OpenAIProvider(),
            GoogleProvider()
        ]
        self._active_provider = None
    
    def get_provider_for_model(self, model_name: str) -> AIModelProvider:
        """Get the appropriate provider for the given model name."""
        # Handle aliases
        if model_name in self.DEFAULT_MODELS:
            model_name = self.DEFAULT_MODELS[model_name]
            
        for provider in self.providers:
            if provider.is_compatible_model(model_name):
                return provider
        
        raise ValueError(f"No provider found for model: {model_name}")
    
    def generate_completion(self, 
                          prompt: str, 
                          model: str = "default", 
                          response_model: Type[BaseModel] = None,
                          **kwargs) -> Any:
        """Generate a completion using the appropriate provider."""
        # Translate default model aliases to actual model names
        if model in self.DEFAULT_MODELS:
            model = self.DEFAULT_MODELS[model]
            
        provider = self.get_provider_for_model(model)
        return provider.generate_completion(prompt, model, response_model, **kwargs)