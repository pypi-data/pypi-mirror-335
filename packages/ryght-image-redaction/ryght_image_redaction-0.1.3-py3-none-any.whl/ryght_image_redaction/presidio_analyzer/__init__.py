# isort: skip_file
"""Presidio analyzer package."""

import logging

from ryght_image_redaction.presidio_analyzer.analysis_explanation import AnalysisExplanation
from ryght_image_redaction.presidio_analyzer.recognizer_result import RecognizerResult
from ryght_image_redaction.presidio_analyzer.dict_analyzer_result import DictAnalyzerResult
from ryght_image_redaction.presidio_analyzer.entity_recognizer import EntityRecognizer
from ryght_image_redaction.presidio_analyzer.local_recognizer import LocalRecognizer
from ryght_image_redaction.presidio_analyzer.pattern import Pattern
from ryght_image_redaction.presidio_analyzer.pattern_recognizer import PatternRecognizer
from ryght_image_redaction.presidio_analyzer.remote_recognizer import RemoteRecognizer
from ryght_image_redaction.presidio_analyzer.recognizer_registry import RecognizerRegistry
from ryght_image_redaction.presidio_analyzer.analyzer_engine import AnalyzerEngine
from ryght_image_redaction.presidio_analyzer.batch_analyzer_engine import BatchAnalyzerEngine
from ryght_image_redaction.presidio_analyzer.analyzer_request import AnalyzerRequest
from ryght_image_redaction.presidio_analyzer.analyzer_utils import PresidioAnalyzerUtils
from ryght_image_redaction.presidio_analyzer.context_aware_enhancers import ContextAwareEnhancer
from ryght_image_redaction.presidio_analyzer.context_aware_enhancers import LemmaContextAwareEnhancer
from ryght_image_redaction.presidio_analyzer.analyzer_engine_provider import AnalyzerEngineProvider

# Define default loggers behavior

# 1. ryght_image_redaction.presidio_analyzer logger

logging.getLogger("presidio-analyzer").addHandler(logging.NullHandler())

# 2. decision_process logger.
# Setting the decision process trace here as we would want it
# to be activated using a parameter to AnalyzeEngine and not by default.

decision_process_logger = logging.getLogger("decision_process")
ch = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s]%(message)s")
ch.setFormatter(formatter)
decision_process_logger.addHandler(ch)
decision_process_logger.setLevel("INFO")
__all__ = [
    "Pattern",
    "AnalysisExplanation",
    "RecognizerResult",
    "DictAnalyzerResult",
    "EntityRecognizer",
    "LocalRecognizer",
    "PatternRecognizer",
    "RemoteRecognizer",
    "RecognizerRegistry",
    "AnalyzerEngine",
    "AnalyzerRequest",
    "ContextAwareEnhancer",
    "LemmaContextAwareEnhancer",
    "BatchAnalyzerEngine",
    "PresidioAnalyzerUtils",
    "AnalyzerEngineProvider",
]
