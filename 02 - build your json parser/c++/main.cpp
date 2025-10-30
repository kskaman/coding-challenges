#include "json_parser.hpp"
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

void print_usage(const char *program_name)
{
    std::cout << "Usage: " << program_name << " <input_file>\n";
}

bool readWholeFile(std::string path, std::string &out)
{
    std::ifstream in(path, std::ios::binary);
    if (!in)
    {
        return false;
    }
    // ostringstream to read the whole file content
    std::ostringstream ss;
    // Read file content into the stringstream
    ss << in.rdbuf();
    // Assign the content to the output string
    out = ss.str();
    return true;
}

bool hasJsonExtension(const std::string &path)
{
    if (path.size() < 5 || path.substr(path.size() - 5) != ".json")
    {
        return false;
    }
    return true;
}

int main(int argc, char **argv)
{
    if (argc < 2)
    {
        print_usage(argv[0]);
        return 2; // usage error / internal error
    }

    std::string input_path = argv[1];

    // Check if the input file has a .json extension
    if (!hasJsonExtension(input_path))
    {
        std::cerr << "Error: Input file must have a .json extension\n";
        return 2; // usage error / internal error
    }

    std::string input;

    if (!readWholeFile(input_path, input))
    {
        std::cerr << "Error: Could not read file " << input_path << "\n";
        return 2; // file read error
    }

    try
    {
        // Parse the JSON
        Lexer lexer(input);
        Parser parser(lexer);
        JsonPtr result = parser.parse();

        // Pretty print the result
        std::cout << result->toString() << std::endl;

        return 0; // success
    }
    catch (const std::exception &e)
    {
        std::cout << "Invalid JSON: " << e.what() << std::endl;
        return 1; // parse error
    }
}