"""
Reframe: A Python package for destigmatizing language related to drug use.

This package provides tools to identify, analyze, and rewrite text
containing stigmatizing language.
"""

# Import from core for backward compatibility
from .core import (
    initialize,
    classify_if_drug,
    classify_if_stigma,
    analyze_text_llm,
    rewrite_to_destigma,
    get_emotion,
    analyze_and_rewrite_text
)

# Import main classes for direct access
from .clients import LLMClient, OpenAIClient, TogetherClient, ClaudeClient, get_client
from .classifiers import BaseClassifier, DrugClassifier, StigmaClassifier
from .analyzers import TextAnalyzer, StyleAnalyzer, EmotionAnalyzer, LLMBasedAnalyzer
from .rewriters import TextRewriter, DestigmatizingRewriter
from .utils import get_model_mapping, get_default_model, determine_client_type, load_user_model_configs

__all__ = [
    # Core functions (backward compatibility)
    'initialize',
    'classify_if_drug',
    'classify_if_stigma',
    'analyze_text_llm',
    'rewrite_to_destigma',
    'get_emotion',
    'analyze_and_rewrite_text',
    
    # Client classes
    'LLMClient',
    'OpenAIClient',
    'TogetherClient',
    'ClaudeClient',
    'get_client',
    
    # Classifier classes
    'BaseClassifier',
    'DrugClassifier',
    'StigmaClassifier',
    
    # Analyzer classes
    'TextAnalyzer',
    'StyleAnalyzer',
    'EmotionAnalyzer',
    'LLMBasedAnalyzer',
    
    # Rewriter classes
    'TextRewriter',
    'DestigmatizingRewriter',
    
    'get_model_mapping',
    'get_default_model',
    'load_user_model_configs'
]