"""
Pacote para análise e extração de dados HTML com BeautifulSoup.
Fornece classes e funções para facilitar a manipulação de documentos HTML.
"""

from .parser import HTMLParser
from .extractors import DataExtractor
from .utils import HTMLUtils

__all__ = [
    'HTMLParser',
    'DataExtractor',
    'HTMLUtils',
]

__version__ = '1.0.0'