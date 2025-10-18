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
    std::ostringstream ss;
    ss << in.rdbuf();
    out = ss.str();
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
    std::string input;

    if (!readWholeFile(input_path, input))
    {
        std::cerr << "Error: Could not read file " << input_path << "\n";
        return 2; // file read error
    }

    std::cout << "Loaded " << input.size() << " bytes from: " << input_path << "\n";
    return 0; // success
}