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
