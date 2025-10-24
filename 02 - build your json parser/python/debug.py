from Lexer import Lexer
from Parser import Parser

# Test simple JSON
text = '{"test": 123}'
print(f"Input: {text}")

try:
    lexer = Lexer(text)
    print("Lexer created successfully")
    
    # Print first few tokens
    for i in range(10):
        token = lexer.get_next_token()
        print(f"Token {i}: {token}")
        if token[0] == 'EOF':
            break
    
    # Reset and test parser
    lexer = Lexer(text)
    parser = Parser(lexer)
    print("Parser created successfully")
    
    result = parser.parse()
    print(f"Parse result: {result}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
