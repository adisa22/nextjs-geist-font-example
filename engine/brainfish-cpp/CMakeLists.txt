cmake_minimum_required(VERSION 3.10)
project(BrainFish VERSION 1.0)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Add compile options
if(MSVC)
    add_compile_options(/W4 /WX)
else()
    add_compile_options(-Wall -Wextra -Wpedantic -Werror)
endif()

# Source files
set(SOURCES
    src/main.cpp
    src/engine.cpp
)

# Header files
set(HEADERS
    src/engine.hpp
)

# Create executable
add_executable(brainfish ${SOURCES} ${HEADERS})

# Include directories
target_include_directories(brainfish PRIVATE src)

# Enable testing
enable_testing()

# Installation
install(TARGETS brainfish DESTINATION bin)
