"""
BrainFish Python - Chess Engine Orchestration Layer
"""

from .engine import BrainFishEngine
from .opening_book import OpeningBook
from .exceptions import BrainFishError

__version__ = "0.1.0"
__all__ = ["BrainFishEngine", "OpeningBook", "BrainFishError"]
