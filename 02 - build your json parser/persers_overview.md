## What Is a Parser?

A **parser** is a program that **reads text** and **converts it into a structured format** that a computer can understand and work with.

Think of a parser as a translator between _raw text_ and _structured data_.  
It doesn't just read; it _understands the structure_ of the text according to specific rules (called a **grammar**).

### Example 1: Parsing a Math Expression

Input:

```
2 + 3 * 5
```

A parser doesn't just read the characters `2`, `+`, `3`, `*`, `5`.  
It understands **how** they’re related - according to grammar rules of arithmetic.

It might produce something like this structured form (called an `Abstract Syntax Tree` or `AST`):

```
      +
     / \
    2   *
       /  \
      3    5
```

## What Is JSON?

**JSON (JavaScript Object Notation)** is a lightweight format for storing and exchanging data.
JSON is a data format used to serialize and transmit structured data over a network connection, often between a server and a web application.

> Serialization means converting data structure or object state into a format that cna be stored or transmitted and reconstructed later.

There are many serialization formats, but JSON is one of the most popular due to its simplicity and human-readability.

Everything in a program is already stored as bits in memory (RAM). For example a python dictionary or a C++ struct

```txt
0x7ffde000: 0x50 0x79 0x54 0x68 ...`
```

The in-memory representation depends on

- programming language
- Operating System
- CPU architecture
- compiler

Different systems may have different endianness (byte order) or different pointer sizes. (Read section 2.1 of Computer Systems: A Programmer's Perspective, 3rd ed).

Serialization translates language-dependent, system-dependent representation into a language and system-independent format (like JSON).
Consider an object in memory:

```c++
struct Person {
    int age;           // 4 bytes
    bool isStudent;    // 1 byte
};
Person p = {27, true};
```

In memory (on a `little-endian` system), it might look like this:

```txt
0x7ffde000: 0x1B 0x00 0x00 0x00 0x01
// age = 27 (0x1B), isStudent = true (0x01)
```

Now if you save this object to a file or send it over a network, another system might not interpret these bytes the same way.

- Big-endian machines would read the integer bytes in reverse order.
- Different languages might have different string encodings.

So, instead we convert this object into a JSON string:

```json
{
  "age": 27,
  "isStudent": true
}
```

ths string is stored as bytes in memory like this:

```txt
7B 22 61 67 65 22 3A 32 37 2C 22 69 73 53 74 75 64 65 6E 74 22 3A 74 72 75 65 7D
```

which corresponds to the ASCII characters:

```txt
{"age":27,"isStudent":true}
```

## What Is a JSON Parser?

A **JSON parser** reads JSON text and **converts it into a data structure** that your program can use - for example, into a **dictionary or map** in your programming language.

### Example 2: What a JSON Parser Does

Input (a `.json` file or string):

```json
{ "name": "Alicia", "age": 2700 }
```

The JSON parser processes this text and outputs:

- In **Python** → `{"name": "Alicia", "age": 2700}`
- In **C++** → maybe an `unordered_map<string, any>` or custom structure
- In **JavaScript** → `{ name: "Alicia", age: 2700 }`

Basically, it turns _plain text_ into a _usable object_.

### Internally, How It Works (High-Level)

A JSON parser works in **two phases**:

#### 1. Lexical Analysis (Tokenization)

It reads raw characters and groups them into **tokens** - the smallest meaningful units.

Example JSON:

```json
{ "name": "Alice", "age": 30 }
```

Tokens:

```
{       -> LEFT_BRACE
"name"  -> STRING
:       -> COLON
"Alice" -> STRING
,       -> COMMA
"age"   -> STRING
:       -> COLON
30      -> NUMBER
}       -> RIGHT_BRACE
```

#### 2. Syntax Analysis (Parsing)

The parser takes these tokens and arranges them according to the **JSON grammar** to produce a structured result - for example, a nested map or object tree.

Using the tokens from above, it builds a structure like:

```txt
object
  |
  +-- "name": "Alice"
  |
  +-- "age": 30
```
