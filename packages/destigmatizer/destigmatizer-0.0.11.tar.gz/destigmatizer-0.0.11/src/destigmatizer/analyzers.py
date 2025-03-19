"""Text analyzers for style and emotion detection."""

import nltk
from typing import Dict, Any, Optional
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag
import string
try:
    from lexicalrichness import LexicalRichness
except ImportError:
    print("Warning: lexicalrichness package not installed. Some text analysis features will be limited.")
    # Provide a simple fallback if the package is not available
    class LexicalRichness:
        def __init__(self, text):
            self.text = text
        def mtld(self, threshold=0.72):
            words = self.text.split()
            return len(set(words)) / max(1, len(words))  # Simple type-token ratio

from abc import ABC, abstractmethod
from .clients import LLMClient


class TextAnalyzer(ABC):
    """Abstract base class for text analyzers."""
    
    @abstractmethod
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze the provided text.
        
        Args:
            text: Text to analyze
            
        Returns:
            dict: Analysis results
        """
        pass


class StyleAnalyzer(TextAnalyzer):
    """Analyzer for text style features."""
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze stylistic features of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            dict: Style analysis results
        """
        # Download required NLTK resources if needed
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger')
            
        # Tokenize sentences and words
        sentences = sent_tokenize(text)
        
        # Punctuation analysis
        punctuation_counts = {key: text.count(key) for key in string.punctuation}
        common_punctuation = ', '.join([p for p, count in punctuation_counts.items() if count > 0])

        # Active vs. Passive Voice
        def is_passive(sentence):
            tagged = pos_tag(word_tokenize(sentence))
            passive = False
            for i in range(len(tagged) - 1):
                if tagged[i][1] in ['was', 'were'] and tagged[i+1][1] == 'VBN':
                    passive = True
            return passive

        passive_sentences = sum(is_passive(sentence) for sentence in sentences)
        passive_voice_usage = "none" if passive_sentences == 0 else "some"

        # Sentence length variability
        sentence_lengths = [len(s.split()) for s in sentences]
        min_length = min(sentence_lengths) if sentence_lengths else 0
        max_length = max(sentence_lengths) if sentence_lengths else 0
        average_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0

        # Lexical diversity
        lex = LexicalRichness(text)
        lex_value = lex.mtld(threshold=0.72)

        return {
            "punctuation_usage": f"moderate, with {common_punctuation} being most frequent",
            "passive_voice_usage": passive_voice_usage,
            "sentence_length_variation": f"ranging from short ({min_length} words) to long ({max_length} words) with an average of {average_length:.1f} words per sentence",
            "lexical_diversity": f"{lex_value:.2f} (MTLD)"
        }


class EmotionAnalyzer(TextAnalyzer):
    """Analyzer for detecting emotions in text."""
    
    def __init__(self, client: Any):
        """Initialize with an LLM client.
        
        Args:
            client: LLM client instance
        """
        self.client = client
        
    def analyze(self, text: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Detect emotions in the provided text.
        
        Args:
            text: Text to analyze
            model: Model to use for analysis
            
        Returns:
            dict: Emotion analysis results
        """
        prompt = """
        Please play the role of an emotion recognition expert. Please provide the most likely emotion that the following text conveys.
        Only one emotion should be provided.
        """
        
        try:
            result = self.client.create_completion(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text}
                ],
                model=model
            )
            emotion = result.lower().strip()
            
            return {
                "primary_emotion": emotion,
            }
        except Exception as e:
            print(f"Error detecting emotion: {e}")
            return {"primary_emotion": "unknown"}


class LLMBasedAnalyzer(TextAnalyzer):
    """Text analyzer that uses LLM for more advanced analysis."""
    
    def __init__(self, client: Any, emotion_analyzer: EmotionAnalyzer, style_analyzer: StyleAnalyzer):
        """Initialize with LLM client and other analyzers.
        
        Args:
            client: LLM client instance
            emotion_analyzer: Emotion analyzer instance
            style_analyzer: Style analyzer instance
        """
        self.client = client
        self.emotion_analyzer = emotion_analyzer
        self.style_analyzer = style_analyzer
        
    def analyze(self, text: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Perform comprehensive text analysis using multiple methods.
        
        Args:
            text: Text to analyze
            model: Model to use for LLM analysis
            
        Returns:
            dict: Combined analysis results
        """
        # Get style analysis
        style_results = self.style_analyzer.analyze(text)
        
        # Get emotion analysis
        emotion_results = self.emotion_analyzer.analyze(text, model=model)
        
        # Combine results
        combined_results = {
            **style_results,
            "top_emotions": emotion_results["primary_emotion"]
        }
        
        return combined_results
