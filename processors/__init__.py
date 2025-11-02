"""
SpinGenius Processors Module
处理器模块
"""

from .html_parser import HTMLParser
from .term_protector import TermProtector

# 相似度检测器是可选的
try:
    from .similarity import SimilarityChecker
    __all__ = ['HTMLParser', 'SimilarityChecker', 'TermProtector']
except ImportError:
    __all__ = ['HTMLParser', 'TermProtector']
