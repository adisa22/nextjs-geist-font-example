"""
FastAPI server for BrainFish chess engine and collaborative opening book.
"""

import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import chess
import asyncio
from pathlib import Path

from brainfish import BrainFishEngine, OpeningBook, BrainFishError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="BrainFish Chess Engine API",
    description="API for chess analysis and collaborative opening book",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class AnalysisRequest(BaseModel):
    fen: str
    depth: Optional[int] = 20
    multipv: Optional[int] = 1
    time_limit: Optional[float] = 1.0

class OpeningBookEntry(BaseModel):
    fen: str
    move: str
    evaluation: Optional[float] = None

class AnalysisResponse(BaseModel):
    analysis: List[Dict]
    book_move: Optional[str] = None

# Global engine instance
engine: Optional[BrainFishEngine] = None
opening_book: Optional[OpeningBook] = None

@app.on_event("startup")
async def startup_event():
    """Initialize engine and opening book on server startup."""
    global engine, opening_book
    try:
        engine = BrainFishEngine()
        await engine.initialize()
        opening_book = OpeningBook()
        logger.info("Engine and opening book initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize engine: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on server shutdown."""
    global engine
    if engine:
        await engine.quit()
        logger.info("Engine shut down successfully")

# Dependency for engine access
async def get_engine():
    """Dependency to get engine instance."""
    if engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    return engine

async def get_opening_book():
    """Dependency to get opening book instance."""
    if opening_book is None:
        raise HTTPException(status_code=503, detail="Opening book not initialized")
    return opening_book

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_position(
    request: AnalysisRequest,
    engine: BrainFishEngine = Depends(get_engine),
    book: OpeningBook = Depends(get_opening_book)
):
    """
    Analyze a chess position.
    """
    try:
        # Check opening book first
        book_move = book.get_move(request.fen)
        
        # Get engine analysis
        analysis = await engine.analyze_position(
            request.fen,
            depth=request.depth,
            multipv=request.multipv,
            time_limit=request.time_limit
        )
        
        return {
            "analysis": analysis,
            "book_move": book_move
        }
    except BrainFishError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/opening-book/add")
async def add_to_opening_book(
    entry: OpeningBookEntry,
    book: OpeningBook = Depends(get_opening_book)
):
    """
    Add a move to the collaborative opening book.
    """
    try:
        success = book.add_move(
            entry.fen,
            entry.move,
            entry.evaluation
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to add move")
        return {"status": "success"}
    except BrainFishError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to add to opening book: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/opening-book/position/{fen}")
async def get_position_info(
    fen: str,
    book: OpeningBook = Depends(get_opening_book)
):
    """
    Get information about a position from the opening book.
    """
    try:
        return book.get_position_info(fen)
    except BrainFishError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get position info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/opening-book/popular")
async def get_popular_positions(
    limit: int = 10,
    book: OpeningBook = Depends(get_opening_book)
):
    """
    Get the most popular positions from the opening book.
    """
    try:
        return book.get_popular_positions(limit)
    except Exception as e:
        logger.error(f"Failed to get popular positions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
