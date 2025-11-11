import shlex
import sys, os
from subprocess import run


IS_WINDOWS = os.name == 'nt'

HELP_TEXT = """\
Built-ins:
  exit                Exit the shell
  cd [path]           Change the current directory (no arg -> home)
  pwd                 Print the current working directory
  clear               Clear the terminal screen
  help [command]      Display this help (optionally for a command)
  echo [text...]      Print arguments as text  
"""

def exit(*_args):
    """Exit the shell."""
    sys.exit(0)

def pwd(*_args):
    """Print the current working directory."""
    try:
        print(os.getcwd())
    except Exception as e:
        print(f"Error retrieving current directory: {e}")

def clear(*_args):
    # Cross platform clear screen
    os.system('cls' if IS_WINDOWS else 'clear')

def help(*args):
    """
    if args provided, show help for that command
    else show general help.
    """
    if not args:
        print(HELP_TEXT)
        return
    
    cmd = args[0]

    info = {
        "exit": "exit — quit the shell.",
        "cd": "cd [path] — change directory (default: home).",
        "pwd": "pwd — print working directory.",
        "clear": "clear — clear terminal screen.",
        "help": "help [command] — display help.",
        "echo": "echo [text...] — print text to stdout.",
    }.get(cmd)

    if info:
        print(info)
    else:
        print(f"No help available for '{cmd}'.\n")

def cd(*args):
    """
    Change the current working directory.
    If no argument is provided, change to the user's home directory.
    """

    if args:
        path = args[0]
        try:
            os.chdir(os.path.expanduser(path))
        except FileNotFoundError:
            print(f"No such directory: {path}")
        except NotADirectoryError:
            print(f"Not a directory: {path}")
        except PermissionError:
            print(f"Permission denied: {path}")
        except Exception as e:
            print(f"Error changing directory: {e}")
        return
    
    # No args, go to home directory
    try:
        home = os.path.expanduser("~")
        os.chdir(home)
    except Exception as e:
        print(f"Error changing to home directory: {e}")

def echo(*args):
    """Print the provided arguments as text."""
    print(" ".join(args))

COMMANDS = {
    "exit": exit,
    "quit": exit,
    "cd": cd,
    "pwd": pwd,
    "clear": clear,
    "help": help,
    "echo": echo,
}


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