"""
Simple JSON Parser - File Input Only
Usage: 
    python main.py <filename>           # Parse JSON from file

Previously supported (now commented out):
    python main.py '<json_string>'      # Parse JSON from string  
    echo '<json_string>' | python main.py  # Parse JSON from pipe
"""
import sys
import os
from Lexer import Lexer
from Parser import Parser


def pretty_print(obj, indent=0):
    """
    Simple pretty printer for parsed JSON objects.
    """
    spaces = "  " * indent
    
    if obj is None:
        return "null"
    elif isinstance(obj, bool):
        return "true" if obj else "false"
    elif isinstance(obj, str):
        return f'"{obj}"'
    elif isinstance(obj, (int, float)):
        return str(obj)
    elif isinstance(obj, list):
        if not obj:
            return "[]"
        result = "[\n"
        for i, item in enumerate(obj):
            result += f"{spaces}  {pretty_print(item, indent + 1)}"
            if i < len(obj) - 1:
                result += ","
            result += "\n"
        result += f"{spaces}]"
        return result
    elif isinstance(obj, dict):
        if not obj:
            return "{}"
        result = "{\n"
        items = list(obj.items())
        for i, (key, value) in enumerate(items):
            result += f'{spaces}  "{key}": {pretty_print(value, indent + 1)}'
            if i < len(items) - 1:
                result += ","
            result += "\n"
        result += f"{spaces}}}"
        return result
    else:
        return str(obj)


def parse_json(text):
    """
    Parse JSON text and return the result.
    """
    try:
        lexer = Lexer(text)
        parser = Parser(lexer)
        result = parser.parse()
        return result, None
    except Exception as e:
        return None, str(e)


def main():
    # # Check if reading from pipe (stdin) - COMMENTED OUT
    # if not sys.stdin.isatty():
    #     # Reading from pipe
    #     text = sys.stdin.read().strip()
    #     if not text:
    #         print("Error: No input provided", file=sys.stderr)
    #         sys.exit(1)
    # elif len(sys.argv) != 2:
    
    # Only accept file inputs
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python main.py <filename>       # Parse JSON from file")
        # print("  python main.py '<json_string>'  # Parse JSON from string")  # COMMENTED OUT
        # print("  echo '<json_string>' | python main.py  # Parse from pipe")  # COMMENTED OUT
        sys.exit(1)
    # else:
    
    filename = sys.argv[1]  # input_arg renamed to filename for clarity
    
    # Check if it's a valid file
    if not os.path.isfile(filename):
        print(f"Error: File '{filename}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Always read from file (no string input allowed)
    # if os.path.isfile(input_arg):  # COMMENTED OUT - always true now
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    # else:  # COMMENTED OUT
    #     # Treat as JSON string  # COMMENTED OUT
    #     text = input_arg  # COMMENTED OUT

    # Parse the JSON
    result, error = parse_json(text)
    
    if error:
        print(f"JSON Parse Error: {error}", file=sys.stderr)
        sys.exit(1)
    else:
        # Pretty print the result
        print(pretty_print(result))


if __name__ == "__main__":
    main()