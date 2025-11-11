import shlex

from ccsh.command_helpers import COMMANDS, run_external

def ccsh():
    while True:
        try:
            line = input("ccsh> ")
        except EOFError:
            return
        except KeyboardInterrupt:
            print()
            continue
    
        if not line.strip():
            continue

        # use shlex to properly parse the command line
        try:
            parts = shlex.split(line)
        except ValueError as e:
            print(f"Error parsing command: {e}")
            continue

        # if command is empty after parsing, skip
        if not parts:
            continue

        cmd, *args = parts

        if cmd in COMMANDS:
            try:
                COMMANDS[cmd](*args)
            except TypeError as e:
                print(f"Error executing command '{cmd}': {e}")
            except SystemExit:
                raise
            except Exception as e:
                print(f"Error executing command '{cmd}': {e}")
            continue

        # External command
        try:
            run_external(line)
        except FileNotFoundError:
            print("command not found")
        except Exception as e:
            print("command not found")
       
if __name__ == "__main__":
    ccsh()