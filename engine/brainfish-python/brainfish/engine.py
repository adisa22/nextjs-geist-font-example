"""
BrainFish Engine Adapter Module
"""

import subprocess
import logging
import chess
import chess.engine
from pathlib import Path
from typing import Optional, List, Dict, Union
from .exceptions import BrainFishError
from .opening_book import OpeningBook

logger = logging.getLogger(__name__)

class BrainFishEngine:
    """
    High-level interface to the BrainFish chess engine.
    Coordinates between C++ engine and Rust integration layer.
    """

    def __init__(self, engine_path: Optional[Path] = None):
        """
        Initialize the BrainFish engine interface.

        Args:
            engine_path: Path to the engine executable. If None, attempts to locate it.
        """
        self.engine_path = engine_path or self._locate_engine()
        self.engine: Optional[chess.engine.SimpleEngine] = None
        self.opening_book = OpeningBook()
        self._initialized = False

    def _locate_engine(self) -> Path:
        """Locate the engine executable in standard locations."""
        # Check common locations
        possible_paths = [
            Path("./build/brainfish"),
            Path("./bin/brainfish"),
            Path("../brainfish-cpp/build/brainfish"),
        ]

        for path in possible_paths:
            if path.exists():
                return path.resolve()

        raise BrainFishError("Could not locate BrainFish engine executable")

    async def initialize(self) -> None:
        """Initialize the engine and prepare it for analysis."""
        if self._initialized:
            logger.warning("Engine already initialized")
            return

        try:
            # Start the engine process
            self.engine = await chess.engine.SimpleEngine.popen_uci(
                str(self.engine_path)
            )
            self._initialized = True
            logger.info("BrainFish engine initialized successfully")
        except Exception as e:
            raise BrainFishError(f"Failed to initialize engine: {e}")

    async def quit(self) -> None:
        """Gracefully shut down the engine."""
        if self.engine:
            await self.engine.quit()
            self._initialized = False
            logger.info("Engine shut down successfully")

    async def analyze_position(
        self,
        position: Union[chess.Board, str],
        depth: int = 20,
        multipv: int = 1,
        time_limit: float = 1.0,
    ) -> List[Dict]:
        """
        Analyze a chess position.

        Args:
            position: Chess position (either Board object or FEN string)
            depth: Maximum analysis depth
            multipv: Number of principal variations to calculate
            time_limit: Time limit for analysis in seconds

        Returns:
            List of analysis results, each containing score and principal variation
        """
        if not self._initialized:
            raise BrainFishError("Engine not initialized")

        # Convert string FEN to board if necessary
        if isinstance(position, str):
            try:
                position = chess.Board(position)
            except ValueError as e:
                raise BrainFishError(f"Invalid FEN string: {e}")

        # First check opening book
        book_move = self.opening_book.get_move(position.fen())
        if book_move:
            logger.info("Found position in opening book")
            return [{
                "source": "opening_book",
                "move": book_move,
                "score": None,
                "pv": [book_move]
            }]

        try:
            # Set up analysis parameters
            limit = chess.engine.Limit(
                depth=depth,
                time=time_limit
            )

            # Perform analysis
            info = await self.engine.analyse(
                position,
                limit,
                multipv=multipv
            )

            # Format results
            results = []
            for pv in info:
                results.append({
                    "source": "engine",
                    "score": pv["score"].relative.score(),
                    "mate": pv["score"].relative.mate(),
                    "pv": [move.uci() for move in pv["pv"]],
                    "depth": pv["depth"]
                })

            return results

        except Exception as e:
            raise BrainFishError(f"Analysis failed: {e}")

    async def get_best_move(
        self,
        position: Union[chess.Board, str],
        time_limit: float = 1.0
    ) -> str:
        """
        Get the best move for a position.

        Args:
            position: Chess position (either Board object or FEN string)
            time_limit: Time limit for calculation in seconds

        Returns:
            Best move in UCI format (e.g., 'e2e4')
        """
        if not self._initialized:
            raise BrainFishError("Engine not initialized")

        # Convert string FEN to board if necessary
        if isinstance(position, str):
            try:
                position = chess.Board(position)
            except ValueError as e:
                raise BrainFishError(f"Invalid FEN string: {e}")

        # Check opening book first
        book_move = self.opening_book.get_move(position.fen())
        if book_move:
            return book_move

        try:
            # Calculate best move
            result = await self.engine.play(
                position,
                chess.engine.Limit(time=time_limit)
            )
            return result.move.uci()

        except Exception as e:
            raise BrainFishError(f"Failed to calculate best move: {e}")

    def update_opening_book(self, fen: str, move: str) -> bool:
        """
        Update the opening book with a new move.

        Args:
            fen: Position in FEN format
            move: Move in UCI format

        Returns:
            True if successful, False otherwise
        """
        try:
            return self.opening_book.add_move(fen, move)
        except Exception as e:
            logger.error(f"Failed to update opening book: {e}")
            return False

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.quit()
