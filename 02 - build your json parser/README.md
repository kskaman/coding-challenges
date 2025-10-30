# Coding Challenge 2 : Build Your JSON Parser

In this challenge, you will build a simple JSON parser from scratch. The goal is to understand the structure of JSON data and how to parse it into a usable format in your programming language of choice.

**Challenge Link :** [Build Your JSON Parser Challenge](https://codingchallenges.fyi/challenges/challenge-json-parser)

## References

- [Medium Article - Building my own JSON Parser - by Saumya Bakshi](https://sbmusing.medium.com/building-my-own-json-parser-a337500e29a1) - python implementation of a JSON parser from scratch.

## Folder Structure

```
.
├── README.md
├── c++
|   └── build.sh - build script
|   └── json_parser.cpp - contains lexer class, parser class and json value classes declarations
|   └── lexer.cpp - contains lexer class implementation
|   └── main.cpp - this file accepts json file path as command line argument and runs the parser
|   └── parser.cpp - contains parser class and json value classes implementations
├── python
│   └── Lexer.py - lexer class implementation
│   └── Parser.py - parser class implementation
│   └── main.py - this file accepts json file path as command line argument and runs the parser
└── testFiles
    └── fail2.json - fail33.json
    └── pass1.json - pass3.json
└── python_implementation.md
└── parser_overview.md
```

## Usage

- Download this folder

#### python

- open folder containing python files in terminal
- run command: `python main.py <path_to_json_file>`

#### c++

- open folder containing c++ files in terminal
- run command: `sh build.sh` to compile the code
- run command: `./json_parser <path_to_json_file>`

## Test Files

The `testFiles` directory contains several JSON files to test your parser. Files named `passX.json` are valid JSON files that your parser should successfully parse, while files named `failX.json` are invalid JSON files that your parser should reject.

## Additional Resources

- For a detailed overview of the parser implementation, refer to `parser_overview.md`.
- For a Python-specific implementation guide, refer to `python_implementation.md`.
- You can also visit the challenge link for more details and instructions.

## Contributing

Feel free to fork this repository and submit pull requests with improvements or bug fixes. Your contributions are welcome!
