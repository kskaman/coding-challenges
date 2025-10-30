#!/bin/bash
# build.sh - Simple build script for Unix/Linux/Mac

echo "Building JSON Parser..."

# Compile all source files and link them
g++ -std=c++14 -Wall -Wextra -O2 -o json_parser main.cpp json_parser.cpp

if [ $? -eq 0 ]; then
    echo "Build successful! Executable: json_parser"
else
    echo "Build failed!"
    exit 1
fi
