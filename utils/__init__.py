"""
ANNA HYPERACTIVE AutoML
Вспомогательные модули
"""

from .automl_engine import SuperAutoML
from .hyperactive_engine import HyperactiveAutoML
from .llm_engine import LLMEngine
from .data_analyzer import DataAnalyzer
from .data_processor import DataProcessor
from .nlp_parser import NLPParser
from .report_generator import ReportGenerator
from .stream_simulator import SensorSimulator
from .music_search import search_music, format_search_results, search_artist, search_mood

__all__ = [
    'SuperAutoML',
    'HyperactiveAutoML', 
    'LLMEngine',
    'DataAnalyzer',
    'DataProcessor',
    'NLPParser',
    'ReportGenerator',
    'SensorSimulator',
    'search_music',
    'format_search_results',
    'search_artist',
    'search_mood'
]

__version__ = '2.1.0'
__author__ = 'Anna Hyperactive AutoML'