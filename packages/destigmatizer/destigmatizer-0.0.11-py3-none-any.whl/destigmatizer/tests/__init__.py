"""
Test package for reframe.

This module exposes the test functions so they can be imported directly
from reframe.tests.
"""

from .test_drug_classifier import test_drug_classifier
from .test_stigma_classifier import test_stigma_classifier
from .test_text_analyzer import test_text_analyzer
from .test_rewriter import test_rewriter
from .test_workflow import test_workflow
from .run_all_tests import run_all_tests, main

__all__ = [
    'test_drug_classifier',
    'test_stigma_classifier',
    'test_text_analyzer',
    'test_rewriter',
    'test_workflow',
    'run_all_tests',
    'main'
]
