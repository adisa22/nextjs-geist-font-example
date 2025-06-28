#include "engine.hpp"
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <unordered_map>

namespace brainfish {

class Engine::Implementation {
public:
    Implementation() : initialized_(false) {}

    bool initialized_;
    std::unordered_map<std::string, std::string> opening_book_;
};

Engine::Engine() : pimpl(std::make_unique<Implementation>()) {}
Engine::~Engine() = default;

bool Engine::initialize(const std::string& config_path) {
    try {
        if (pimpl->initialized_) {
            return true;  // Already initialized
        }

        initializeOpeningBook();
        pimpl->initialized_ = true;
        return true;
    } catch (const std::exception& e) {
        std::cerr << "Initialization error: " << e.what() << std::endl;
        return false;
    }
}

std::string Engine::processCommand(const std::string& command) {
    if (!pimpl->initialized_) {
        return "error engine not initialized";
    }

    std::istringstream iss(command);
    std::string cmd;
    iss >> cmd;

    if (cmd == "uci") {
        return "id name BrainFish\nid author BlackBoxAI\nuciok\n";
    } else if (cmd == "isready") {
        return "readyok\n";
    } else if (cmd == "quit") {
        return "quit\n";
    }

    return "unknown command\n";
}

std::string Engine::analyzePosition(const std::string& fen, int depth) {
    if (!pimpl->initialized_) {
        return "error engine not initialized";
    }

    if (!validateFEN(fen)) {
        return "error invalid fen";
    }

    // TODO: Implement actual position analysis
    // This is a placeholder that would be replaced with actual Stockfish integration
    return "info depth " + std::to_string(depth) + " score cp 100 pv e2e4 e7e5\n";
}

std::string Engine::getBestMove(const std::string& fen, int time_ms) {
    if (!pimpl->initialized_) {
        return "error engine not initialized";
    }

    if (!validateFEN(fen)) {
        return "error invalid fen";
    }

    // First check opening book
    std::string book_move = queryOpeningBook(fen);
    if (!book_move.empty()) {
        return "bestmove " + book_move + "\n";
    }

    // TODO: Implement actual best move calculation
    // This is a placeholder that would be replaced with actual Stockfish integration
    return "bestmove e2e4\n";
}

std::string Engine::queryOpeningBook(const std::string& fen) {
    auto it = pimpl->opening_book_.find(fen);
    if (it != pimpl->opening_book_.end()) {
        return it->second;
    }
    return "";
}

bool Engine::updateOpeningBook(const std::string& fen, const std::string& move) {
    if (!validateFEN(fen)) {
        return false;
    }

    // TODO: Implement validation of move format
    pimpl->opening_book_[fen] = move;
    return true;
}

bool Engine::validateFEN(const std::string& fen) {
    // TODO: Implement proper FEN validation
    // This is a basic check that should be expanded
    return !fen.empty() && fen.find('/') != std::string::npos;
}

void Engine::initializeOpeningBook() {
    // TODO: Load opening book from file
    // For now, just initialize with some basic positions
    pimpl->opening_book_["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"] = "e2e4";
}

} // namespace brainfish
