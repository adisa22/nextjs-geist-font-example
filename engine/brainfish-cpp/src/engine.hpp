#ifndef BRAINFISH_ENGINE_HPP
#define BRAINFISH_ENGINE_HPP

#include <string>
#include <vector>
#include <memory>

namespace brainfish {

class Engine {
public:
    Engine();
    ~Engine();

    // Initialize the engine with optional parameters
    bool initialize(const std::string& config_path = "");

    // Process UCI command and return response
    std::string processCommand(const std::string& command);

    // Analyze current position
    std::string analyzePosition(const std::string& fen, int depth = 20);

    // Get best move for current position
    std::string getBestMove(const std::string& fen, int time_ms = 1000);

    // Handle opening book operations
    std::string queryOpeningBook(const std::string& fen);
    bool updateOpeningBook(const std::string& fen, const std::string& move);

private:
    class Implementation;
    std::unique_ptr<Implementation> pimpl;  // PIMPL idiom for better binary compatibility

    // Internal helper methods
    bool validateFEN(const std::string& fen);
    void initializeOpeningBook();
};

} // namespace brainfish

#endif // BRAINFISH_ENGINE_HPP
