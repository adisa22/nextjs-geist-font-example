# BrainFish Chess Engine

A sophisticated chess analysis application that combines the power of C++, Rust, and Python to provide high-performance chess analysis with collaborative opening book features.

## Features

- High-performance chess engine core (C++)
- Rust integration layer for enhanced functionality
- Python orchestration with FastAPI server
- Collaborative opening book system
- Modern web interface for analysis

## Project Structure

```
.
├── engine/
│   ├── brainfish-cpp/           # C++ engine core
│   │   ├── src/
│   │   │   ├── engine.cpp
│   │   │   ├── engine.hpp
│   │   │   └── main.cpp
│   │   └── CMakeLists.txt
│   │
│   ├── brainfish-rust/         # Rust integration layer
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   └── main.rs
│   │   └── Cargo.toml
│   │
│   └── brainfish-python/       # Python orchestration
│       ├── brainfish/
│       │   ├── __init__.py
│       │   ├── engine.py
│       │   ├── exceptions.py
│       │   └── opening_book.py
│       ├── server/
│       │   └── main.py
│       └── setup.py
│
└── src/                        # Frontend components
    ├── app/
    └── components/
```

## Prerequisites

- C++17 compatible compiler
- Rust 1.54 or later
- Python 3.8 or later
- CMake 3.10 or later
- Node.js 14 or later

## Building from Source

1. Build the C++ engine:
   ```bash
   cd engine/brainfish-cpp
   mkdir build && cd build
   cmake ..
   make
   ```

2. Build the Rust integration:
   ```bash
   cd engine/brainfish-rust
   cargo build --release
   ```

3. Install Python package:
   ```bash
   cd engine/brainfish-python
   pip install -e .
   ```

4. Install frontend dependencies:
   ```bash
   npm install
   ```

## Running the Application

1. Start the FastAPI server:
   ```bash
   cd engine/brainfish-python/server
   uvicorn main:app --reload
   ```

2. Start the frontend development server:
   ```bash
   npm run dev
   ```

The application will be available at `http://localhost:3000`.

## API Documentation

The FastAPI server provides the following endpoints:

- `POST /analyze` - Analyze a chess position
- `POST /opening-book/add` - Add a move to the collaborative opening book
- `GET /opening-book/position/{fen}` - Get information about a position
- `GET /opening-book/popular` - Get popular positions from the opening book

Detailed API documentation is available at `http://localhost:8000/docs` when the server is running.

## Opening Book Collaboration

The collaborative opening book system allows users to:
- Contribute new moves and variations
- View popular positions and lines
- Access community-contributed analysis
- Track move frequencies and evaluations

## Development

### Running Tests

1. C++ tests:
   ```bash
   cd engine/brainfish-cpp/build
   ctest
   ```

2. Rust tests:
   ```bash
   cd engine/brainfish-rust
   cargo test
   ```

3. Python tests:
   ```bash
   cd engine/brainfish-python
   pytest
   ```

### Code Style

- C++: Follow Google C++ Style Guide
- Rust: Use `rustfmt` and `clippy`
- Python: Follow PEP 8 and use `black` formatter

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on Stockfish chess engine
- Uses modern web technologies for the frontend
- Inspired by collaborative chess analysis platforms
