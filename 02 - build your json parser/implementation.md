# Implementation Steps

1. Get the file path from command line arguments and ensure it ends with `.json`.
2. Read the entire content of the specified JSON file into a string.

## References

- [Medium Article - Building my own JSON Parser - by Saumya Bakshi](https://sbmusing.medium.com/building-my-own-json-parser-a337500e29a1) - python implementation of a JSON parser from scratch.

# JSON Parser - How It Works Step by Step

## Overview

Your JSON parser has 3 main parts that work together:

1. **Lexer** - Breaks text into tokens (like words)
2. **Parser** - Understands the grammar and builds data structures
3. **Main** - Handles files and coordinates everything

Think of it like reading a sentence: first you identify words (lexer), then you understand grammar (parser).

JSON file can contain:

- Strings (e.g. "hello")
- Numbers (e.g. 123, -45.67, 1e10)
- null
- booleans (true, false)

and complex structures:

- Objects (dictionaries) `{ "key": "value" }`
- Arrays (lists) `[1, 2, 3]`

A Parser asks the lexer for tokens one by one and based on the token type, it decides what to do next (like building an object or array).

For example if lexer gives token

- `STRING`, parser knows it's a string value
- `NUMBER`, parser knows it's a number value
- `NULL`, parser knows it's a null value
- `TRUE`/`FALSE`, parser knows it's a boolean value

- `LBRACE` (`{`), parser knows to start building an object.
- `LBRACKET` (`[`), parser knows to start building an array.

Thus, based on current token identified by lexer, parser constructors appropriate data structures recursively.

## Part 1: The Lexer (Tokenizer)

### What Does It Do?

The lexer reads JSON text **character by character** and tags them to meaningful **tokens** (defined as per context).

**Example:**

```json
{ "name": "John", "age": 25 }
```

As lexer reads this text character by character, the lexer produces tokens like:

```
LBRACE: {
STRING: name
COLON: :
STRING: John
COMMA: ,
STRING: age
COLON: :
NUMBER: 25
RBRACE: }
EOF: (end)
```

If it encounters invalid characters or sequences while reading the text, it raises errors with line/column info.

### How It Works

#### Step 1: Initialize

```python
def __init__(self, text):
    self._text = text           # The JSON string to parse
    self._pos = 0              # Current position (starts at 0)
    self._line = 1             # Current line number
    self._column = 1           # Current column number
    self.current_char = text[0] # Current character we're looking at
```

#### Step 2: Move Through Text

```python
def _next(self):
    self._pos += 1             # Move to next position
    if self.current_char == '\n':
        self._line += 1        # New line found
        self._column = 1       # Reset column
    else:
        self._column += 1      # Move to next column

    # Update current_char to the new position
    if self._pos >= len(self._text):
        self.current_char = None  # End of text
    else:
        self.current_char = self._text[self._pos]
```

#### Step 3: Skip Whitespace

```python
def _skip_whitespace(self):
    # Skip spaces, tabs, newlines between tokens
    while self.current_char is not None and self.current_char.isspace():
        self._next()
```

#### Step 4: Recognize Tokens

**Simple Characters (one character = one token):**

```python
if self.current_char == '{':
    self._next()
    return ('LBRACE', '{')   # Left brace token

if self.current_char == '}':
    self._next()
    return ('RBRACE', '}')   # Right brace token
```

**Strings (more complex):**

```python
def _string(self):
    result = ''
    self._next()  # Skip opening quote "

    while self.current_char != '"':  # Until closing quote
        if ord(self.current_char) < 32:
            self.error()  # Reject control characters like \n, \t

        if self.current_char == '\\':  # Escape sequence
            self._next()  # Skip the \
            if self.current_char == 'n':
                result += '\n'  # Convert \n to actual newline
            elif self.current_char == 't':
                result += '\t'  # Convert \t to actual tab
            # ... handle other escapes
        else:
            result += self.current_char  # Normal character

        self._next()

    self._next()  # Skip closing quote "
    return result
```

**Numbers (with validation):**

```python
def _number(self):
    result = ''

    # Handle negative sign
    if self.current_char == '-':
        result += '-'
        self._next()

    # First digit rules (no leading zeros except 0 itself)
    if self.current_char == '0':
        result += '0'
        self._next()
        if self.current_char and self.current_char.isdigit():
            self.error()  # 013 is invalid! (leading zero)
    elif self.current_char.isdigit():
        # Regular digits 1-9, then any digits
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self._next()

    # Handle decimal point
    if self.current_char == '.':
        result += '.'
        self._next()
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self._next()

    # Handle scientific notation (1e10, 2.5E-3)
    if self.current_char and self.current_char.lower() == 'e':
        result += self.current_char
        self._next()
        if self.current_char in '+-':
            result += self.current_char
            self._next()
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self._next()

    # Convert to number
    if '.' in result or 'e' in result.lower():
        return float(result)
    return int(result)
```

Thus, lexer identifies tokens one by one until the entire text is processed, using functions like `_string()`, `_number()`, and simple character checks.

## Part 2: The Parser (Grammar Understanding)

### What Does It Do?

The parser takes tokens from the lexer and builds the actual data structure (dict, list, etc.) following JSON grammar rules.

### Key Concept: Recursive Descent

The parser works by calling functions that call other functions, like:

- `parse_object()` calls `parse_value()`
- `parse_value()` might call `parse_array()`
- `parse_array()` calls `parse_value()` again

### How It Works

#### Step 1: Initialize

```python
def __init__(self, lexer):
    self.lexer = lexer
    self.current_token = self.lexer.get_next_token()  # Get first token
```

#### Step 2: Check and Consume Tokens

```python
def _check_token(self, expected_type):
    if self.current_token[0] == expected_type:
        self.current_token = self.lexer.get_next_token()  # Move to next token
    else:
        self.lexer.error()  # Wrong token type!
```

#### Step 3: Parse Different Value Types

**Parse Object `{}`:**

```python
def _parse_object(self):
    obj = {}
    self._check_token('LBRACE')  # Expect {

    if self.current_token[0] == 'RBRACE':  # Empty object {}
        self._check_token('RBRACE')
        return obj

    while True:
        # Get key
        key = self._parse_string()  # Must be string
        self._check_token('COLON')  # Expect :

        # Get value
        value = self._parse_value()  # Any JSON value
        obj[key] = value

        # What's next?
        if self.current_token[0] == 'COMMA':
            self._check_token('COMMA')
            # Check for errors like trailing comma {key: value,}
            if self.current_token[0] == 'RBRACE':
                self.lexer.error()  # Trailing comma not allowed!
        elif self.current_token[0] == 'RBRACE':
            self._check_token('RBRACE')
            break
        else:
            self.lexer.error()  # Expected comma or }

    return obj
```

**Parse Array `[]`:**

```python
def _parse_array(self):
    array = []
    self._check_token('LBRACKET')  # Expect [

    if self.current_token[0] == 'RBRACKET':  # Empty array []
        self._check_token('RBRACKET')
        return array

    while True:
        # Get value
        value = self._parse_value()  # Any JSON value
        array.append(value)

        # What's next?
        if self.current_token[0] == 'COMMA':
            self._check_token('COMMA')
            # Check for errors like [1, 2, ,] or [1, 2,]
            if self.current_token[0] == 'COMMA' or self.current_token[0] == 'RBRACKET':
                self.lexer.error()  # Double comma or trailing comma!
        elif self.current_token[0] == 'RBRACKET':
            self._check_token('RBRACKET')
            break
        else:
            self.lexer.error()  # Expected comma or ]

    return array
```

**Parse Any Value (The Central Function):**

```python
def _parse_value(self):
    token_type = self.current_token[0]

    if token_type == 'LBRACE':      # {
        return self._parse_object()
    elif token_type == 'LBRACKET':  # [
        return self._parse_array()
    elif token_type == 'STRING':    # "text"
        return self._parse_string()
    elif token_type == 'NUMBER':    # 123
        return self._parse_number()
    elif token_type == 'TRUE':      # true
        return self._parse_boolean()
    elif token_type == 'FALSE':     # false
        return self._parse_boolean()
    elif token_type == 'NULL':      # null
        return self._parse_null()
    else:
        self.lexer.error()  # Invalid token!
```

#### Step 4: Main Parse Function

```python
def parse(self):
    result = self._parse_value()  # Parse the main JSON value

    # Make sure nothing is left over
    if self.current_token[0] != 'EOF':
        self.lexer.error()  # Extra content like: {"a":1} "extra"

    return result
```

## Part 3: Putting It All Together

### Example Walkthrough: `{"name": "John"}`

#### Lexer Phase:

```
Position 0: { → Token: ('LBRACE', '{') -> start building an object using _parse_object()
Position 1: " → Start string parsing using lexer._string()
Position 2-5: name → Build string "name"
Position 6: " → End string → Token: ('STRING', 'name')
Position 7: : → Token: ('COLON', ':')
Position 8: (space) → Skip whitespace
Position 9: " → Start string parsing
Position 10-13: John → Build string "John"
Position 14: " → End string → Token: ('STRING', 'John')
Position 15: } → Token: ('RBRACE', '}') -> finish object
End → Token: ('EOF', None)
```

#### Parser Phase:

```
1. parse() calls _parse_value()
2. Current token is 'LBRACE', so call _parse_object()
3. _parse_object() expects '{', gets it
4. _parse_object() calls _parse_string() → gets "name"
5. _parse_object() expects ':', gets it
6. _parse_object() calls _parse_value() → calls _parse_string() → gets "John"
7. _parse_object() expects '}', gets it
8. Return {'name': 'John'}
9. parse() checks for EOF
10. Return final result: {'name': 'John'}
```

### Error Detection

- **Line/Column tracking** - Shows exactly where errors occur
- **Leading zero validation** - Rejects `013` (only `0` allowed)
- **Control character detection** - Rejects unescaped `\n`, `\t` in strings
- **Trailing comma detection** - Rejects `[1,2,]` and `{"a":1,}`
- **Double comma detection** - Rejects `[1,,2]`
- **EOF validation** - Rejects `{"a":1} extra content`

### Advanced JSON Support

- **Scientific notation** - Handles `1e10`, `2.5E-3`
- **Unicode escapes** - Handles `\u0041` (becomes 'A')
- **All escape sequences** - `\"`, `\\`, `\/`, `\b`, `\f`, `\n`, `\r`, `\t`
- **Negative numbers** - Handles `-123`, `-0.5`

## The Flow in Simple Terms

1. **Read file** -> Get JSON text string
2. **Create Lexer** -> Give it the text
3. **Create Parser** -> Give it the lexer
4. **Parse** -> Parser asks lexer for tokens, builds result
5. **Return result** -> Python dict/list/string/number/bool/None
