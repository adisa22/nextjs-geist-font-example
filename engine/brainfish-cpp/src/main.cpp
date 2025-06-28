#include "engine.hpp"
#include <iostream>
#include <string>
#include <memory>

int main() {
    try {
        // Create and initialize the engine
        auto engine = std::make_unique<brainfish::Engine>();
        if (!engine->initialize()) {
            std::cerr << "Failed to initialize engine" << std::endl;
            return 1;
        }

        std::string line;
        // Main UCI protocol loop
        while (std::getline(std::cin, line)) {
            // Process UCI commands
            std::string response = engine->processCommand(line);
            
            // Output the response
            std::cout << response << std::flush;

            // Check for quit command
            if (line == "quit") {
                break;
            }
        }

        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Fatal error: " << e.what() << std::endl;
        return 1;
    }
}
