# `run` command from `subprocess` module

Every time your computer runs a program - whether its chrome, Notepad, or python itself - operating system creates a process.

> A **process** is an independent running program with its own memory space, code and resources.

In python, when we run a python script, script itself is a process ( the **parent process**). If we want to run another program (like git, ping etc) from inside python script, we need to create a new process for that program - a **child process**.

## `subprocess` module

The **subprocess** module lets python code to :

- Start new programs
- Send input to them
- Read output from them
- Wait for them to finish
- Check their exit status

`subprocess.run()` is the most recommended function to create new processes. It runs a command, waits for it to complete, then returns a `CompletedProcess` instance.

**Example 1: Running a simple command**

```python
from subprocess import run
run(["echo", "Hello, World!"])
```

This will print "Hello, World!" to the console. This runs exactly as if you typed `echo Hello, World!` in your terminal.

**Example 2: Capturing output**

```python
from subprocess import run
result = run(["echo", "Hello, World!"], capture_output=True, text=True)
print("Captured Output:", result.stdout)
```

`capture_output=True` means "store the command's output instead of printing it to the console".
`text=True` means "treat the output as text (string) instead of bytes".
`result` is a `CompletedProcess` object that contains information about the executed command, including its output.

Output we get will be:

```py
Captured Output: Hello, World!
```

> ## What we are doing in our shell implementation
>
> ```py
> from subprocess import run
> import sys
>
> def ccsh():
>     cmd = input("ccsh> ").strip()
>     run(cmd, stdin=sys.stdin ,stdout=sys.stdout, stderr=sys.stderr)
> if __name__ == "__main__":
>     ccsh()
> ```
>
> `cmd` refers to command you type in the shell prompt.
> This command connects terminal's input/output to the child process we create using `run()`.
> `stdin=sys.stdin` connects the standard input of the child process to the terminal's input.
> `stdout=sys.stdout` connects the standard output of the child process to the terminal's output
> `stderr=sys.stderr` connects the standard error of the child process to the terminal's error output.
>
> Then it waits for the command to complete before returning control back to the shell.

## Step 2 - Handling Multiple Commands and Exit

To handle multiple commands one after another, we need to put the command input and execution inside a loop. This way, after executing one command, the shell will prompt for another command.

> `sys.exit(0)`
>
> The `sys.exit(0)` function is used to exit from Python. The argument `0` indicates that the program is terminating without any errors. In the context of a shell implementation, it allows users to exit the shell cleanly when they type the "exit" command.

## Handling non-existent commands

When a user types a command that does not exist, the `subprocess.run()` function raises a `FileNotFoundError`. To handle this gracefully, we can use a try-except block around the `run()` call. If a `FileNotFoundError` is caught, we can print an error message to inform the user that the command was not found.

## running commands without arguments

When we are on linux or bash shell, we can simply use

```py
subprocess.run(cmd, stdout=sys.stdout, stdin=sys.stdin, stderr=sys.stderr)
```

What this does ?

## Running Commands with arguments

> shelex: The `shlex` module in Python provides a way to split a string into a list of tokens in a way that is similar to how a Unix shell would parse command-line input. This is particularly useful when you want to handle commands with arguments, as it correctly handles quoted strings and escaped characters.
>
> For example, consider the command string:
>
> ```py
> cmd_line = 'echo "Hello, World!"'
> ```
>
> Using `shlex.split()` on this string will produce the following list of tokens:
>
> ```py
> import shlex
> tokens = shlex.split(cmd_line)
> print(tokens)  # Output: ['echo', 'Hello, World!']
> ```
>
> Here, `shlex.split()` correctly identifies that "Hello, World!" is a single argument to the `echo` command, even though it contains a space. This allows us to pass the command
>
> Without `shlex`, if we simply used `cmd_line.split()`, it would incorrectly split the argument into two separate tokens: `['echo', '"Hello,', 'World!"']`, which would not work as intended when passed to `subprocess.run()`.

> `SystemExit`: Raised when:
>
> - You call `sys.exit(0)` in your `exit()` built-in, or
> - Any library internally calls `exit()`.
>
> If you don’t handle it, `sys.exit()` will actually **terminate your Python process**. That's correct for an "exit" command, but not if some other error accidentally triggers it.
>
> That's why we sometimes catch it separately - to **allow exit to work** but still prevent unwanted shutdowns elsewhere.

> `KeyboardInterrupt`: Raised when:
>
> - The user hits `Ctrl+C` (or `Delete` on some systems) to interrupt the program.
>   If you don’t handle it, the default behavior is to terminate the program and print a traceback.
>   Catching it allows you to:
> - Gracefully handle user interruptions without crashing.
> - Clean up resources or save state before exiting.

> `EOFError`: Raised when:
>
> - The input() function hits an end-of-file condition (EOF) without reading any data. This typically happens when the user sends an EOF signal (like `Ctrl+D` on Unix/Linux or `Ctrl+Z` on Windows) to indicate that there is no more input.
>   If you don’t handle it, the program will terminate with an error message.
>   Catching it allows you to:
> - Gracefully handle the end-of-input scenario.

> `TypeError / ValueError`: Raised when:
>
> - The arguments provided to a function are of the wrong type (TypeError) or have an inappropriate value (ValueError).
>   If you don’t handle them, the program will terminate with an error message.
>   Catching them allows you to:
> - Provide user-friendly error messages.
> - Prompt the user to correct their input without crashing the program.
>   In the context of a shell implementation, catching these exceptions helps ensure that the shell remains stable and user-friendly, even when unexpected input or errors occur.
