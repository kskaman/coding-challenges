# Implementation Notes - ccwc (Custom Word Count Tool)

## What We're Building

We are implementing a clone of the Unix `wc` (word count) command called `ccwc`. This tool counts various statistics in text files:

### Core Functionality

- **Line count** (`-l`): Counts newline characters (`\n`)
- **Word count** (`-w`): Counts sequences of non-whitespace characters
- **Byte count** (`-c`): Counts raw bytes in the file
- **Character count** (`-m`): Counts Unicode code points (UTF-8 characters)

The tool must match the behavior of the standard Unix `wc` command.

## Concepts

#### 1. **Raw Bytes**

A raw byte is the smallest unit of data in a file, represented as 8 bits. It is the unprocessed, exact binary data stored in the file. When reading files in binary mode, we read these raw bytes directly without any interpretation or transformation (like newline conversion - In text mode, some systems (like Windows) convert \r\n (carriage return + newline) into \n. This is not desirable when counting bytes or processing UTF-8.). This is crucial for accurate byte counting and proper handling of binary files. UTF-8 encodes characters as sequence of 1-4 raw bytes

#### 2. **Unicode code points and UTF-8 Encoding**

- `Uncode code point` : A Unicode code point is a unique number assigned to each character in the Unicode standard. It represents a single character, which may be encoded in one or more bytes in UTF-8.

- `UTF-8 Encoding`: Before UTF-8, different systems used various encoding schemes (like ASCII, ISO-8859, etc.), which caused compatibility issues when sharing text across platforms or languages. Unicode was introduced to unify all characters into a single standard.
  UTF-8 encodes characters using 8-bit units (bytes):
- **1 byte**: For ASCII characters (0-127)
- **2 bytes**: For extended Latin characters
- **3 bytes**: For most non-Latin scripts (e.g., chinese, Arabic)
- **4 bytes**: For rare symbols and emojis (e.g., 🚀, 🎉)

`Key Difference`: `UTF-8` is how the `code points` are encoded into bytes, while the `code points` themselves are the `abstract identifiers`.
_Example_: Let’s take the emoji `😀 (grinning face)`: Unicode Code Point: `U+1F600` - This is the abstract number assigned to the emoji. UTF-8 Encoding: `F0 9F 98 80` (4 bytes) - This is how the code point is stored or transmitted in a file or over a network.

`UTF-8 Bit Patterns`: To know how many bytes a UTF-8 character uses, we can look at the leading bits of the first byte:

- 1-byte character: `0xxxxxxx` (0-127, ASCII)
- 2-byte character: `110xxxxx 10xxxxxx`
- 3-byte character: `1110xxxx 10xxxxxx 10xxxxxx`
- 4-byte character: `11110xxx 10xxxxxx 10xxxxxx 10xxxxxx`
  Thus any (2 to 4)-byte character can be identified by checking that first byte starts with `110`, `1110`, or `11110` respectively, and the subsequent bytes start with `10`. Continuation bytes, bytes that follow starting byte of a 2-4 byte character, start with `10`, thus we know this byte is not the start of a new character.

`How this helps in calculating character count`: When reading each byte, if the byte does not start with `10` (i.e., `(b & 0xC0) != 0x80`), it indicates the start of a new UTF-8 character. By counting these starting bytes, we can accurately determine the number of Unicode characters in the file.

## Code Explanations

### Code Overview

We keep flag variables to track which counts are requested (lines, words, bytes, characters).
The main counting logic is encapsulated in the `count_all_stream` function, which processes an input stream and updates a `Counts` struct with the results based on the selected flags.

We also have a `count_file` function to handle file opening and error checking.

Thus user can either input from stdin or provide file paths as command line arguments.

### **count_all_stream**

This function reads the input stream byte by byte, updating the counts based on the content.

```cpp
static bool count_all_stream(istream &in, Counts &out)
```

The function takes an input stream reference and Count structure reference to store the results.
It returns `true` on success and `false` on read error.

> `static` limits the function's scope to the current file, preventing name clashes in larger projects.

```cpp
const size_t BUF = 64 * 1024;
```

we read in chunks of 64KB for efficiency.

```cpp
    std::vector<char> buf(BUF);
```

- In C++, char is the fundamental type for representing a byte of data. It is guaranteed to be 1 byte (8 bits) on all platforms, making it the natural choice for reading raw data from files or streams.
- Functions like `std::istream::read()` and `std::ostream::write()` expect a `char*` pointer for reading and writing data. Using char ensures seamless integration with these standard I/O functions.
- char can represent both text (ASCII characters) and raw binary data, making it versatile for different use cases.

- Why Not Use Other Types?

1. `int` or `short`: These types are larger than 1 byte, which would waste memory and require additional processing to handle individual bytes.
2. `uint8_t`: While uint8_t (from <cstdint>) is equivalent to unsigned char, it is not guaranteed to work with standard I/O functions like `std::istream::read()`, which expect a `char*` pointer.
3. `std::byte`: `std::byte` (introduced in C++17) is specifically designed for raw binary data, but it cannot be directly used with standard I/O functions without casting.

```cpp
bool in_word = false;
```

A flag to track if we are currently inside a word. This helps in counting words correctly.

```cpp
    while (true)
    {
        in.read(reinterpret_cast<char *>(buf.data()), static_cast<std::streamsize>(buf.size()));
```

`in.read(char*, streamsize)` performs unformatted , raw reads.
we read a chunk of data from the input stream into the buffer.

The type `std::streamsize` is a signed integral type used to represent the number of characters transferred in an I/O operation or the size of an I/O buffer. It is used as a signed counterpart of `std::size_t`.

if the

```cpp
        std::streamsize got = in.gcount();
        if (got <= 0)
            break;
```

`istream::gcount()` returns the number of characters extracted by the last unformatted input operation. It returns a non-positive value
On normal EOF, `got` will be `0`, causing the loop to break. If there is an error we will have return value `got` to be `0` along with positive evaluation of expression `!in && !in.eof()`. It won't be negative.

```cpp
        out.bytes += static_cast<u64>(got);
```

we update the byte count with the number of bytes read.

```cpp
        for (std::streamsize i = 0; i < got; ++i)
        {
            char ch = buf[static_cast<size_t>(i)];

            // -l: lines
            if (sel.l && ch == '\n')
            {
                out.lines++;
            }

            // -w: word transitions (use unsigned char for ctype)
            if (sel.w)
            {
                unsigned char uch = static_cast<unsigned char>(ch);
                bool is_space = (std::isspace(uch) != 0);
                if (is_space)
                {
                    in_word = false;
                }
                else if (!in_word)
                {
                    out.words++;
                    in_word = true;
                }
            }

            // -m: UTF-8 code points — count non-continuation bytes
            if (sel.m)
            {
                unsigned char uch = static_cast<unsigned char>(ch);
                if ((uch & 0xC0) != 0x80)
                {
                    out.chars++;
                }
            }
        }
```

the variable `bool is_space` helps determine if the current byte is a whitespace character.

- `std::isspace` is a function template in C++ used to determine if a given character is a whitespace character.

```cpp
        if (!in && !in.eof())
            return false; // real read error
    }
```

A last we check for read errors. If the stream is in a failed state and not at EOF, we return false indicating a read error. Otherwise, we return true on successful completion.

> 3. **count_file** Function: The `count_file` function opens a file and calls `count_all_stream` to perform the counting.

```cpp
static bool count_file(const string &path, Counts &out)
{
    ifstream in(path, std::ios::binary);
    if (!in)
        return false;
    return count_all_stream(in, out);
}
```

`ifstream in(path, std::ios::binary);`:

- `ifstream`: This is an input file stream class in C++ used for reading data from files. It is part of the `<fstream>` header.
- `path`: This is a string variable that contains the path to the file you want to open.
- `std::ios::binary`: This is a flag that specifies the mode in which the file should be opened. The `std::ios::binary` flag indicates that the file should be opened in binary mode, meaning that the data will be read as raw bytes without any translation (like newline conversion). This is important for accurately counting bytes and handling binary files.

- If file opening fails (e.g., file does not exist), we get boolean `false` from the `if (!in)` check, and the function returns `false` to indicate the error.

### Platform-Specific Code: Handling Windows Binary Mode

```cpp
#ifdef _WIN32
#include <io.h>
#include <fcntl.h>
#endif
```

- **Purpose**: These headers and the associated code are used to handle platform-specific behavior on Windows. By default, Windows treats files and standard input/output as text streams, which can cause issues when working with raw binary data (e.g., for byte counting).
  - **`<io.h>`**: Provides functions like `_setmode` and `_fileno` to manipulate file modes.
  - **`<fcntl.h>`**: Defines constants like `_O_BINARY` for setting binary mode.

```cpp
#ifdef _WIN32
    // If we'll read stdin (no filename provided), switch stdin to binary so -c is exact.
    if (argc == 1 || (argc == 2 && parse_flags(argv[1]).any()))
    {
        _setmode(_fileno(stdin), _O_BINARY);
    }
#endif
```

- **Explanation**:
  - **`_setmode`**: Changes the mode of a file descriptor. Here, it is used to set the mode of `stdin` to binary (`_O_BINARY`).
  - **`_fileno`**: Retrieves the file descriptor for a given stream (e.g., `stdin`).
  - **Why This Is Needed**:
    - On Windows, text mode translates line endings (`\r\n` to `\n`), which can lead to incorrect byte counts when using the `-c` flag.
    - Switching to binary mode ensures that raw bytes are read without any translation, making the behavior consistent with Unix-like systems.

---

### Headers Used

```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cctype>
#include <cstdint>
#include <iomanip>
```

- **Purpose of Each Header**:
  1. **`<iostream>`**:
     - Provides standard input/output streams (`std::cin`, `std::cout`, `std::cerr`).
     - Used for printing results and error messages.
  2. **`<fstream>`**:
     - Provides file stream classes (`std::ifstream`, `std::ofstream`).
     - Used for reading input files in binary mode.
  3. **`<vector>`**:
     - Provides the `std::vector` container.
     - Used as a buffer for reading chunks of data from the input stream.
  4. **`<string>`**:
     - Provides the `std::string` class.
     - Used for handling file paths and command-line arguments.
  5. **`<cctype>`**:
     - Provides character classification functions like `std::isspace`.
     - Used for detecting whitespace characters when counting words.
  6. **`<cstdint>`**:
     - Provides fixed-width integer types like `uint64_t`.
     - Used for defining the `Counts` struct with precise integer sizes.
  7. **`<iomanip>`**:
     - Provides I/O manipulators like `std::setw`.
     - Used for formatting output to align columns.

---

### Explanation of `main` Function Logic

The `main` function serves as the entry point for the `ccwc` tool. It handles command-line arguments, determines the mode of operation, and invokes the appropriate functions to perform counting. Below is a detailed explanation of its logic:

#### Key Steps in the `main` Function

1. **Disable Synchronization with C I/O**:

   ```cpp
   std::ios::sync_with_stdio(false);
   ```

   - Disables synchronization between C and C++ standard streams for improved performance.

2. **Handle Windows-Specific Binary Mode**:

   ```cpp
   #ifdef _WIN32
   if (argc == 1 || (argc == 2 && parse_flags(argv[1]).any()))
   {
       _setmode(_fileno(stdin), _O_BINARY);
   }
   #endif
   ```

   - On Windows, switches `stdin` to binary mode to ensure accurate byte counting when reading from standard input.

3. **Case 1: No Arguments**:

   ```cpp
   if (argc == 1)
   {
       Sel sel = default_sel_if_empty(Sel{});
       Counts c;
       if (!count_stream(std::cin, sel, c))
       {
           cerr << "ccwc: failed to read from stdin\n";
           return 1;
       }
       print_selected(sel, c);
       return 0;
   }
   ```

   - Defaults to reading from `stdin` with the default selection (`-l -w -c`).
   - Calls `count_stream` to process the input and `print_selected` to display the results.

4. **Case 2: One Argument**:

   ```cpp
   if (argc == 2)
   {
       string a1 = argv[1];
       Sel sel = parse_flags(a1);
       if (sel.any())
       {
           Counts c;
           if (!count_stream(std::cin, sel, c))
           {
               cerr << "ccwc: failed to read from stdin\n";
               return 1;
           }
           print_selected(sel, c);
           return 0;
       }
       else
       {
           Sel def = default_sel_if_empty(Sel{});
           Counts c;
           if (!count_file(a1, def, c))
           {
               cerr << "ccwc: cannot open file: " << a1 << "\n";
               return 1;
           }
           print_selected(def, c, &a1);
           return 0;
       }
   }
   ```

   - **Flags Only**: If the argument is a valid flag (e.g., `-lwm`), reads from `stdin` and processes the input based on the selected flags.
   - **Filename**: If the argument is not a valid flag, treats it as a filename and processes the file with the default selection (`-l -w -c`).

5. **Case 3: Two Arguments**:

   ```cpp
   if (argc == 3)
   {
       string flags = argv[1];
       string path = argv[2];
       Sel sel = parse_flags(flags);
       if (!sel.any())
       {
           usage();
           return 1;
       }

       Counts c;
       if (!count_file(path, sel, c))
       {
           cerr << "ccwc: cannot open file: " << path << "\n";
           return 1;
       }
       print_selected(sel, c, &path);
       return 0;
   }
   ```

   - Expects a combination of flags and a filename.
   - Parses the flags and processes the specified file based on the selected options.

6. **Invalid Usage**:
   ```cpp
   usage();
   return 1;
   ```
   - If the arguments do not match any of the above cases, displays the usage information and exits with an error code.

## Summary of Key Functions Used

- **`parse_flags`**: Parses command-line flags and returns a `Sel` structure indicating the selected options.
- **`default_sel_if_empty`**: Provides default options (`-l -w -c`) if no flags are specified.
- **`count_stream`**: Processes an input stream and updates the `Counts` structure.
- **`count_file`**: Opens a file and calls `count_stream` to process its contents.
- **`print_selected`**: Displays the selected counts in the canonical order (`lines`, `words`, `bytes`, `characters`).
- **`usage`**: Prints usage information for the tool.

This structure ensures that the `ccwc` tool handles various input scenarios gracefully, providing accurate results and helpful error messages.
