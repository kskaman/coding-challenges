class Parser:
    def __init__(self, lexer):
        """
        Initialize the parser with a lexer.
        :param lexer: An instance of the Lexer class.
        """
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def _check_token(self, token_type):
        """
        Check if the current token matches the expected type.
        :param token_type: The expected token type.
        """
        if self.current_token[0] == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.lexer.error()

    def _parse_boolean(self):
        """
        Parse a boolean value from the input string.
        :return: True or False
        """
        token = self.current_token
        if token[0] == 'TRUE':
            self._check_token('TRUE')
            return True
        elif token[0] == 'FALSE':
            self._check_token('FALSE')
            return False

    def _parse_null(self):
        """
        Parse a null value from the input string.
        :return: None
        """
        token = self.current_token
        if token[0] == 'NULL':
            self._check_token('NULL')
            return None
        
    def _parse_string(self):
        """
        Parse a string value from the input string.
        :return: The parsed string value.
        """
        token = self.current_token
        if token[0] == 'STRING':
            self._check_token('STRING')
            return token[1]
        
    def _parse_number(self):
        """
        Parse a number value from the input string.
        :return: The parsed number value.
        """
        token = self.current_token
        if token[0] == 'NUMBER':
            self._check_token('NUMBER')
            return token[1]
        
    def _parse_array(self):
        """
        Parse an array from the input string.
        :return: The parsed array.
        """
        array = []
        self._check_token('LBRACKET')
        if self.current_token[0] == 'RBRACKET':
            self._check_token('RBRACKET')
            return array
        while True:
            value = self._parse_value()
            array.append(value)
            if self.current_token[0] == 'COMMA':
                self._check_token('COMMA')
                # Check for consecutive commas or trailing comma
                if self.current_token[0] == 'COMMA' or self.current_token[0] == 'RBRACKET':
                    self.lexer.error()
                continue
            elif self.current_token[0] == 'RBRACKET':
                self._check_token('RBRACKET')
                break
            else:
                self.lexer.error()

        return array
    
    def _parse_object(self):
        """
        Parse an object from the input string.
        :return: The parsed object.
        """
        obj = {}
        self._check_token('LBRACE')
        if self.current_token[0] == 'RBRACE':
            self._check_token('RBRACE')
            return obj
        while True:
            key = self._parse_string()
            self._check_token('COLON')
            value = self._parse_value()
            obj[key] = value
            if self.current_token[0] == 'COMMA':
                self._check_token('COMMA')
                # Check for consecutive commas or trailing comma
                if self.current_token[0] == 'COMMA' or self.current_token[0] == 'RBRACE':
                    self.lexer.error()
                continue
            elif self.current_token[0] == 'RBRACE':
                self._check_token('RBRACE')
                break
            else:
                self.lexer.error()

        return obj
    
    def _parse_value(self):
        """
        Parse a value from the input string.
        :return: The parsed value.
        """
        token_type = self.current_token[0]
        if token_type == 'LBRACE':
            return self._parse_object()
        elif token_type == 'LBRACKET':
            return self._parse_array()
        elif token_type == 'STRING':
            return self._parse_string()
        elif token_type == 'NUMBER':
            return self._parse_number()
        elif token_type == 'TRUE' or token_type == 'FALSE':
            return self._parse_boolean()
        elif token_type == 'NULL':
            return self._parse_null()
        else:
            self.lexer.error()


    def parse(self):        
        """
        Parse the input string and return the resulting data structure.
        :return: The parsed data structure.
        """
        result = self._parse_value()
        # Ensure no extra content after valid JSON
        if self.current_token[0] != 'EOF':
            self.lexer.error()
        return result
    
    