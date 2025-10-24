class Lexer:
    def __init__(self, text):
        """
        Initialize the lexer with the input text.
        :param text: The input JSON string to be tokenized.
        self._text - The input JSON string.
        self._line - The current line number in the input string.
        self._column - The current column number in the input string.
        self._pos - The current position in the input string.
        self.current_char - The character at the current position.
        """
        self._text = text
        self._line = 1
        self._column = 1
        self._pos = 0
        self.current_char = self._text[self._pos] if self._text else None

    def _next(self):
        """
        Advance the 'pos' pointer and update the 'current_char'.
        If the end of the input string is reached, set 'current_char' to None.
        """
        self._pos += 1
        if self.current_char == '\n':
            self._line += 1
            self._column = 1
        else:
            self._column += 1

        if self._pos >= len(self._text):
            self.current_char = None
        else:
            self.current_char = self._text[self._pos]
            
        

    def _skip_whitespace(self):
        """
        Skip whitespace characters in the input string.
        Advances the 'pos' pointer until a non-whitespace character is found.
        """
        while self.current_char is not None and self.current_char.isspace():
            self._next()


    def _number(self):
        """
        Parse a number from the input string.
        Handles integers, floats, and scientific notation.
        Validates JSON number format (no leading zeros).
        :return: The parsed number as an int or float.
        """
        result = ''
        
        # Handle negative sign
        if self.current_char == '-':
            result += self.current_char
            self._next()
        
        # Parse integer part with leading zero validation
        if self.current_char == '0':
            result += self.current_char
            self._next()
            # After '0', next char must be '.', 'e', 'E', or end of number
            if self.current_char and self.current_char.isdigit():
                self.error()  # Reject leading zeros like 013, 01.5
        elif self.current_char and self.current_char.isdigit():
            # Parse remaining digits (1-9 followed by any digits)
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self._next()
        else:
            self.error()  # No digits found

        # Parse decimal part
        if self.current_char == '.':
            result += self.current_char
            self._next()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self._next()

        # Parse scientific notation (e or E)
        if self.current_char and self.current_char.lower() == 'e':
            result += self.current_char
            self._next()
            
            # Handle + or - after e/E
            if self.current_char and self.current_char in '+-':
                result += self.current_char
                self._next()
            
            # Parse exponent digits
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self._next()

        # Convert to appropriate type
        if '.' in result or 'e' in result.lower():
            return float(result)
        return int(result)
    
    def _string(self):
        """
        Parse a string from the input string.
        Handles escape sequences including unicode.
        :return: The parsed string without the enclosing quotes.
        """
        result = ''
        self._next()  # Skip the opening quote

        while self.current_char is not None and self.current_char != '"':
            # Check for unescaped control characters (ASCII 0-31)
            # ord is a built-in Python function that returns 
            # the Unicode code point (numeric value) of a character.
            # numeric unicode value less than 32 are control characters
            if ord(self.current_char) < 32:
                self.error()  # Reject unescaped control characters like \n, \t, etc.
            
            if self.current_char == '\\':
                self._next()  # Skip backslash
                if self.current_char == '"':
                    result += '"'
                elif self.current_char == '\\':
                    result += '\\'
                elif self.current_char == '/':
                    result += '/'
                elif self.current_char == 'b':
                    result += '\b'
                elif self.current_char == 'f':
                    result += '\f'
                elif self.current_char == 'n':
                    result += '\n'
                elif self.current_char == 'r':
                    result += '\r'
                elif self.current_char == 't':
                    result += '\t'
                elif self.current_char == 'u':
                    # Handle unicode escape \uXXXX
                    self._next()
                    hex_chars = ''
                    for _ in range(4):
                        if self.current_char and self.current_char in '0123456789abcdefABCDEF':
                            hex_chars += self.current_char
                            self._next()
                        else:
                            self.error()
                    result += chr(int(hex_chars, 16))
                    continue  # Don't advance again
                else:
                    self.error()
            else:
                result += self.current_char
            self._next()

        self._next()  # Skip the closing quote
        return result
    
    def _peek(self):
        """
        Return the _next character without advancing the position.
        :return: The _next character or None if at end of input.
        """
        peek_pos = self._pos + 1
        if peek_pos >= len(self._text):
            return None
        return self._text[peek_pos]

    def _boolean(self):
        """
        Parse a boolean value from the input string.
        :return: The parsed boolean value (True or False).
        """
        if self._text[self._pos:self._pos + 4] == 'true':
            for _ in range(4):
                self._next()
            return 'TRUE'
        elif self._text[self._pos:self._pos + 5] == 'false':
            for _ in range(5):
                self._next()
            return 'FALSE'
        
        
    def _null(self):
        """
        Parse a null value from the input string.
        :return: 'NULL' token type
        """
        if self._text[self._pos:self._pos + 4] == 'null':
            for _ in range(4):
                self._next()
            return 'NULL'
    
        
    def error(self):
        """
        Raise an exception for invalid characters.
        """
        raise Exception(f"Invalid Syntax: at line {self._line} column {self._column} of file.")

    
    def get_next_token(self):
        """
        Tokenize the input string and return the _next token.
        :return: The _next token in the input string.
        """
        while self.current_char is not None:
            if self.current_char.isspace():
                self._skip_whitespace()
                continue

            if self.current_char == '{':
                self._next()
                return ('LBRACE', '{')

            if self.current_char == '}':
                self._next()
                return ('RBRACE', '}')

            if self.current_char == '[':
                self._next()
                return ('LBRACKET', '[')

            if self.current_char == ']':
                self._next()
                return ('RBRACKET', ']')

            if self.current_char == ':':
                self._next()
                return ('COLON', ':')

            if self.current_char == ',':
                self._next()
                return ('COMMA', ',')

            if self.current_char == '"':
                value = self._string()
                return ('STRING', value)

            if self.current_char.isdigit() or (self.current_char == '-' and self._peek() and self._peek().isdigit()):
                value = self._number()
                return ('NUMBER', value)

            if self.current_char == 't' or self.current_char == 'f':
                token_type = self._boolean()
                return (token_type, token_type)

            if self.current_char == 'n':
                token_type = self._null()
                return (token_type, None)

            self.error()

        return ('EOF', None)
    