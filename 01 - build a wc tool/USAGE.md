# usage

1. Download ccwc.cpp from the repository.
2. Save it to your local machine. Make sure you have a C++ compiler installed (like g++ or clang++).
3. Open terminal from the directory containing the ccwc.cpp.
4. Build the program using:
   ```
   g++ ccwc.cpp -o ccwc
   ```
5. Run the command with desired options and file names. For example:

   - Count lines, words, and bytes in a file:
     ```
     ./ccwc filename.txt
     ```
   - Count characters in a file:
     ```
     ./ccwc -m filename.txt
     ```
   - Count lines in a file:
     ```
     ./ccwc -l filename.txt
     ```
   - Count words in a file:

   ```
   ./ccwc -w filename.txt
   ```

   - Count bytes in a file:
     ```
     ./ccwc -c filename.txt
     ```
   - Combine multiple options:

     ```
     ./ccwc -l -w -c filename.txt
     ```

     or

     ```./ccwc -lwc filename.txt

     ```

   - Count multiple files:
     ```
     ./ccwc -l -w -c file1.txt file2.txt
     ```
   - Read from standard input (stdin):
     ```
     cat filename.txt | ./ccwc -l -w -c
     ```

6. The output will display the counts in a formatted manner, similar to the Unix `wc` command:
