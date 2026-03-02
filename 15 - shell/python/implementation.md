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

Now, when working on a shell implementation, above `run` command will not work as expected. Why ? If we type `ls` on linux or `dir` on windows, it will throw an error like this:

```py
FileNotFoundError: [Errno 2] No such file or directory: 'ls'
```

Consider following code:

```py
cmd = input("ccsh> ").strip()
run(cmd, stdin=sys.stdin ,stdout=sys.stdout, stderr=sys.stderr)
```

- It reads what user types in the shell prompt and stores it in `cmd`.
- It passes the string to `run()` to execute.
- `subprocess.run()` tries to find an executable file with that name in system's `PATH` and runs it.
  On Linus/maxOS, there's an actual executable called `bin/ls`. On Windows, there is no `ls` executable - `dir` command is a built in command of `cmd.exe` shell. So, `subprocess.run()` cannot find an executable file named `ls` or `dir`, resulting in a `FileNotFoundError`.

So what do we do. We will first check on what operating system we are in using

```py
IS_WINDOWS = os.name == 'nt'
```

Here, `os.name == 'nt'` checks if the operating system is Windows (where 'nt' stands for Windows NT). If the condition is true, `IS_WINDOWS` will be set to `True`, indicating that the code is running on a Windows system. If the condition is false, `IS_WINDOWS` will be set to `False`, indicating that the code is running on a non-Windows system (like Linux or macOS).

Then we will run commands differently based on operating system. We will add one more argument `shell=True` to `run()` command on windows.

```py
run(cmd, stdin=sys.stdin ,stdout=sys.stdout, stderr=sys.stderr, shell=IS_WINDOWS)
```

The `shell` argument in the `subprocess.run()` function specifies whether to execute the command through the shell. When `shell=True`, the command is executed through the shell (like `cmd.exe` on Windows or `/bin/sh` on Unix-like systems). This allows you to use shell features like built-in commands, pipes, and environment variable expansion.

Next step will be to write logic that decides how to handle what user types.
We can categorize commands as follow:

1. **built-in commands** : commands that are implemented directly in the shell itself like `cd`, `exit`, `pwd` etc. We implement using `os` module functions.
2. **external commands** : commands that are separate executable files like `ls`, `git`, `ping` etc. We implement using `subprocess.run()`.
3. **Custom ccsh commands** : commands that are specific to our shell like `help`, `history` etc. We implement using custom functions.

At the end, we have invalid command handling logic to catch any command that does not fall into above categories.

## Handling Built-in Commands

Built-in commands are commands that are implemented directly within the shell itself, rather than being separate executable files. Examples of built-in commands include `cd` (change directory), `exit` (exit the shell), and `pwd` (print working directory).

Now, how do we implement built-in commands in our shell using python ?

First we define a list of external commands and custom commands that our shell will support. We will check whether the command user typed is in that list or not. If not, we will use `subprocess.run()` to execute it as an external command. If it's not a command that is recognized by the shell, `subprocess.run()` will raise a `FileNotFoundError`, which we can catch and handle gracefully.

#### defining commands that we will support using python libraries like `os` and `sys`

```py
EXTERNAL_COMMANDS = ['ls', 'dir', 'ping', 'git', 'echo', 'cat', 'mkdir', 'rm']
CUSTOM_COMMANDS = ['help', 'history']
```

Now, if command user typed is not in above lists, we will invoke `subprocess.run()` to execute it as an external command.

We can do something like this:

```py
# function to process a single line command (for testing)
def process_line(line: str) -> int:
    """
    Parse and execute one command line.
    Return an int exit code (0 on success).
    """
    parts = shlex.split(line)
    if not parts:
        return 0

    cmd, *args = parts
    if cmd in COMMANDS:
        COMMANDS[cmd](*args)  # may raise SystemExit for 'exit'
        return 0
    return run_external(line) or 0
```

In above code we first split the command line into parts using `shlex.split()`. Then we check if the command (`cmd`) is in our list of supported commands (`COMMANDS`). If it is, we call the corresponding function with any arguments (`*args`). If the command is not recognized, we call `run_external(line)` to execute it as an external command using `subprocess.run()` as follows :

```py
def run_external(raw_line: str):
    """
    Run an external command line.
    - On Windows: use shell=True so cmd built-ins (dir, cls) work.
      Also map 'ls' to 'dir' for convenience.
    - On Unix: split into argv and run with shell=False.
    """

        # map 'ls' to 'dir' at the beginning of the line
    stripped = raw_line.strip()
    if stripped == "ls" and IS_WINDOWS:
        raw_line = raw_line.replace("ls", "dir", 1)

    if stripped == "cmd":
        raise Exception("Refusing to run 'cmd' to avoid nested shells.")
    return run(
        raw_line,
        shell=IS_WINDOWS,
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
    ).returncode
```

Above code handles external commands as follows:

- It first checks if the command is `ls` on Windows, and if so, it replaces it with `dir` for compatibility.
- It also prevents running the `cmd` command to avoid nested shells.
- Finally, it uses `subprocess.run()` to execute the command, passing the appropriate arguments to connect the standard input, output, and error streams.
- It returns the exit code of the command using `.returncode`.
- If the command is not found, `subprocess.run()` will raise a `FileNotFoundError`, which we can catch and handle gracefully in our shell implementation.

> `sys.exit(0)`
>
> The `sys.exit(0)` function is used to exit from Python. The argument `0` indicates that the program is terminating without any errors. In the context of a shell implementation, it allows users to exit the shell cleanly when they type the "exit" command.

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
