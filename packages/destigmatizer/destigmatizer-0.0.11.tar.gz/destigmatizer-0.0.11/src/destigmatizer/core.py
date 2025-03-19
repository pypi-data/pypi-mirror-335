"""Core functionality for the reframe package."""

from typing import Tuple, Dict, Any, Optional, Union
from .clients import get_client
from .classifiers import DrugClassifier, StigmaClassifier
from .analyzers import StyleAnalyzer, EmotionAnalyzer, LLMBasedAnalyzer
from .rewriters import DestigmatizingRewriter
from .clients import detect_client_type
from .utils import get_model_mapping


def initialize(api_key: Optional[str] = None, client: Optional[Any] = None, 
              client_type: Optional[str] = None) -> Any:
    """
    Initialize and return a client for the Reframe library.
    
    Args:
        api_key: API key for the language model service
        client: Pre-configured client instance
        client_type: Type of client ("openai", "together", or "claude")
        
    Returns:
        Any: Client instance
        
    Raises:
        ValueError: If neither api_key nor client is provided, or if client_type is unsupported
    """
    if client:
        return client
    elif api_key:
        return get_client(client_type, api_key)
    else:
        raise ValueError("Either api_key or client must be provided")


def classify_if_drug(text: str, client: Any, model: Optional[str] = None,
                    retries: int = 2) -> str:
    """
    Classify if text contains drug-related content.
    
    Args:
        text: Text content to classify
        client: Client instance
        model: Model to use
        retries: Number of retries on failure
        
    Returns:
        str: 'D' for drug-related, 'ND' for non-drug-related, 'skipped' on error
    """
    drug_classifier = DrugClassifier(client)
    return drug_classifier.classify(text, model=model, retries=retries)


def classify_if_stigma(text: str, client: Any, model: Optional[str] = None,
                      retries: int = 2) -> str:
    """
    Classify if text contains stigmatizing language related to drug use.
    
    Args:
        text: Text content to classify
        client: Client instance
        model: Model to use
        retries: Number of retries on failure
        
    Returns:
        str: Classification result with explanation if stigmatizing
    """
    stigma_classifier = StigmaClassifier(client)
    return stigma_classifier.classify(text, model=model, retries=retries)


def analyze_text_llm(text: str, client: Any, model: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze text style and emotion.
    
    Args:
        text: Text to analyze
        client: Client instance
        model: Model to use
        
    Returns:
        dict: Analysis results
    """
    style_analyzer = StyleAnalyzer()
    emotion_analyzer = EmotionAnalyzer(client)
    analyzer = LLMBasedAnalyzer(client, emotion_analyzer, style_analyzer)
    return analyzer.analyze(text, model=model)


def get_emotion(text: str, client: Any, model: Optional[str] = None,
               temperature: float = 0, retries: int = 2) -> str:
    """
    Detect the primary emotion in text.
    
    Args:
        text: Text to analyze
        client: Client instance
        model: Model to use
        temperature: Sampling temperature
        retries: Number of retries on failure
        
    Returns:
        str: Detected emotion
    """
    emotion_analyzer = EmotionAnalyzer(client)
    result = emotion_analyzer.analyze(text, model=model)
    return result.get("primary_emotion", "unknown")


def rewrite_to_destigma(text: str, explanation: str, style_instruct: str,
                        model: Optional[str] = None, client: Any = None, 
                        retries: int = 2) -> str:
    """
    Rewrite text to remove stigmatizing language.
    
    Args:
        text: Text to rewrite
        explanation: Explanation of stigma from classifier
        style_instruct: Style instructions to maintain
        step: Rewriting step (1 or 2)
        model: Model to use
        client: Client instance
        retries: Number of retries on failure
        
    Returns:
        str: Rewritten text
    """
    client_type = detect_client_type(client)
    mapped_model = get_model_mapping(model, client_type)
    
    rewriter = DestigmatizingRewriter(client)
    return rewriter.rewrite(
        text=text,
        explanation=explanation,
        style_instruct=style_instruct,
        model=mapped_model,
        retries=retries
    )
    
def analyze_and_rewrite_text(text: str, client: Any, model: Optional[str] = None, retries: int = 2) -> str:
    """
    Analyze and rewrite text in a single workflow.
    
    This function encapsulates the entire reframe workflow:
    1. Classify if the text is drug-related
    2. If drug-related, classify if the text contains stigmatizing language
    3. If stigmatizing, analyze the text style and emotion
    4. If stigmatizing, rewrite to remove stigmatizing language
    
    Args:
        text: Text to analyze and potentially rewrite
        client: Client instance (from reframe.initialize())
        model: Model to use for all operations
        retries: Number of retries on failure
        
    Returns:
        str: The rewritten text if stigmatizing and drug-related,
             otherwise returns the original text
    """
    # Step 1: Classify if drug-related
    print("Step 1: Classifying drug-related content...")
    drug_result = classify_if_drug(text, client, model, retries)
    
    # If not drug-related, return the original text
    if drug_result != 'D':
        print("Text is not drug-related. Skipping further analysis.")
        return text
    
    # Step 2: Classify if stigmatizing
    print("Step 2: Checking for stigmatizing language...")
    stigma_result = classify_if_stigma(text, client, model, retries)
    
    # Check if text is stigmatizing (starts with 's')
    is_stigmatizing = stigma_result.startswith('s')
    
    # If not stigmatizing, return the original text
    if not is_stigmatizing:
        print("No stigmatizing content detected. Skipping further analysis.")
        return text
    
    # Step 3: Analyze text style
    print("Step 3: Analyzing text style and emotion...")
    style_result = analyze_text_llm(text, client, model)
        
    # Step 4: Rewrite to remove stigma
    print("Step 4: Rewriting stigmatizing content...")
    # Extract explanation part from stigma classification
    if ', ' in stigma_result:
        _, explanation = stigma_result.split(', ', 1)
    else:
        explanation = stigma_result
    
    # Convert style result to string for the rewriter
    style_instruct = str(style_result)
    
    # Rewrite the text
    rewritten_text = rewrite_to_destigma(
        text=text,
        explanation=explanation,
        style_instruct=style_instruct,
        model=model,
        client=client,
        retries=retries
    )
    
    return rewritten_text
