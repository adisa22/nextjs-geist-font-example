"""
Custom exceptions for the BrainFish engine.
"""

class BrainFishError(Exception):
    """Base exception for all BrainFish-related errors."""
    pass

class EngineNotFoundError(BrainFishError):
    """Raised when the engine executable cannot be found."""
    pass

class EngineInitializationError(BrainFishError):
    """Raised when the engine fails to initialize."""
    pass

class InvalidFENError(BrainFishError):
    """Raised when an invalid FEN string is provided."""
    pass

class AnalysisError(BrainFishError):
    """Raised when position analysis fails."""
    pass

class OpeningBookError(BrainFishError):
    """Raised when there's an error with the opening book operations."""
    pass
