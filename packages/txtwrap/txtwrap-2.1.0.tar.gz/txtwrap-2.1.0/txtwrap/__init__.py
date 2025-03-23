"""
A simple text wrapping tool.
"""

# Supports only in Python 3.3+

from .txtwrap import (
    version,
    LOREM_IPSUM_WORDS, LOREM_IPSUM_SENTENCES, LOREM_IPSUM_PARAGRAPHS,
    TextWrapper,
    mono, word, wrap, align, fillstr, printwrap,
    indent, dedent,
    shorten
)

__version__ = version
__author__ = 'azzammuhyala'
__license__ = 'MIT'
__all__ = [
    'LOREM_IPSUM_WORDS',
    'LOREM_IPSUM_SENTENCES',
    'LOREM_IPSUM_PARAGRAPHS',
    'TextWrapper',
    'mono',
    'word',
    'wrap',
    'align',
    'fillstr',
    'printwrap',
    'indent',
    'dedent',
    'shorten'
]