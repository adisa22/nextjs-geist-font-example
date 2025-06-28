"""
Opening book management for BrainFish engine.
Handles storage and retrieval of opening moves, supporting collaborative expansion.
"""

import json
import logging
import chess
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from .exceptions import OpeningBookError

logger = logging.getLogger(__name__)

class OpeningBook:
    """
    Manages the chess opening book database with support for collaborative updates.
    """

    def __init__(self, book_path: Optional[Path] = None):
        """
        Initialize the opening book manager.

        Args:
            book_path: Path to the opening book JSON file. If None, uses default location.
        """
        self.book_path = book_path or Path("data/opening_book.json")
        self.positions: Dict[str, Dict] = {}
        self._load_book()

    def _load_book(self) -> None:
        """Load the opening book from disk."""
        try:
            if self.book_path.exists():
                with open(self.book_path, 'r') as f:
                    self.positions = json.load(f)
                logger.info(f"Loaded {len(self.positions)} positions from opening book")
            else:
                logger.info("No existing opening book found, starting fresh")
                self.positions = {}
                self._save_book()  # Create the initial empty book
        except Exception as e:
            logger.error(f"Failed to load opening book: {e}")
            self.positions = {}

    def _save_book(self) -> None:
        """Save the opening book to disk."""
        try:
            # Ensure the directory exists
            self.book_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.book_path, 'w') as f:
                json.dump(self.positions, f, indent=2)
            logger.info(f"Saved {len(self.positions)} positions to opening book")
        except Exception as e:
            raise OpeningBookError(f"Failed to save opening book: {e}")

    def get_move(self, fen: str) -> Optional[str]:
        """
        Get the best move for a position from the opening book.

        Args:
            fen: Position in FEN format

        Returns:
            Move in UCI format if found, None otherwise
        """
        try:
            # Validate FEN
            chess.Board(fen)
        except ValueError as e:
            raise OpeningBookError(f"Invalid FEN string: {e}")

        position_data = self.positions.get(fen)
        if not position_data:
            return None

        # Return the most popular move
        moves = position_data.get("moves", {})
        if not moves:
            return None

        # Sort moves by frequency and evaluation
        best_move = max(
            moves.items(),
            key=lambda x: (x[1]["frequency"], x[1].get("evaluation", 0))
        )[0]

        return best_move

    def add_move(self, fen: str, move: str, evaluation: Optional[float] = None) -> bool:
        """
        Add or update a move in the opening book.

        Args:
            fen: Position in FEN format
            move: Move in UCI format
            evaluation: Optional engine evaluation of the position

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate FEN and move
            board = chess.Board(fen)
            move_obj = chess.Move.from_uci(move)
            if move_obj not in board.legal_moves:
                raise OpeningBookError(f"Illegal move: {move}")

            # Initialize position if not exists
            if fen not in self.positions:
                self.positions[fen] = {
                    "moves": {},
                    "total_games": 0
                }

            # Initialize move if not exists
            if move not in self.positions[fen]["moves"]:
                self.positions[fen]["moves"][move] = {
                    "frequency": 0,
                    "evaluation": evaluation,
                    "last_updated": datetime.now().isoformat()
                }

            # Update move data
            move_data = self.positions[fen]["moves"][move]
            move_data["frequency"] += 1
            if evaluation is not None:
                move_data["evaluation"] = evaluation
            move_data["last_updated"] = datetime.now().isoformat()

            # Update total games counter
            self.positions[fen]["total_games"] += 1

            # Save updates to disk
            self._save_book()
            return True

        except Exception as e:
            logger.error(f"Failed to add move to opening book: {e}")
            return False

    def get_position_info(self, fen: str) -> Dict:
        """
        Get detailed information about a position.

        Args:
            fen: Position in FEN format

        Returns:
            Dictionary containing position information
        """
        try:
            # Validate FEN
            chess.Board(fen)
        except ValueError as e:
            raise OpeningBookError(f"Invalid FEN string: {e}")

        if fen not in self.positions:
            return {
                "moves": {},
                "total_games": 0
            }

        return self.positions[fen]

    def get_popular_positions(self, limit: int = 10) -> List[Dict]:
        """
        Get the most frequently played positions.

        Args:
            limit: Maximum number of positions to return

        Returns:
            List of position data sorted by frequency
        """
        sorted_positions = sorted(
            self.positions.items(),
            key=lambda x: x[1]["total_games"],
            reverse=True
        )

        return [
            {"fen": fen, **data}
            for fen, data in sorted_positions[:limit]
        ]

    def export_book(self, output_path: Optional[Path] = None) -> Path:
        """
        Export the opening book to a file.

        Args:
            output_path: Optional custom path for the export

        Returns:
            Path to the exported file
        """
        if output_path is None:
            output_path = self.book_path.parent / f"opening_book_export_{datetime.now():%Y%m%d}.json"

        try:
            with open(output_path, 'w') as f:
                json.dump(self.positions, f, indent=2)
            logger.info(f"Exported opening book to {output_path}")
            return output_path
        except Exception as e:
            raise OpeningBookError(f"Failed to export opening book: {e}")
