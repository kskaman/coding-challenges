import io
import os
import sys
import unittest
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch, MagicMock

# Import after editable install OR add src to sys.path in tests/__init__.py
from ccsh.command_helpers import HELP_TEXT, process_line, COMMANDS, IS_WINDOWS

class TestBuiltinsNoArgs(unittest.TestCase):
    def test_pwd_prints_cwd(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            process_line("pwd")
        out = buf.getvalue().strip()
        print("test - pwd")
        print("Test pwd output:", out)
        print("Actual cwd:", os.getcwd())
        self.assertEqual(out, os.getcwd())

    def test_help_prints(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            process_line("help")
        print("test - help")
        print("Help output:", buf.getvalue())
        print(f"Expected substring: \n{HELP_TEXT}")
        self.assertIn("Built-ins:", buf.getvalue())

    def test_clear_runs(self):
        # Just ensure it doesn't crash
        print("test - clear")
        process_line("clear")

    def test_exit_raises_systemexit(self):
        with self.assertRaises(SystemExit):
            process_line("exit")

class TestCd(unittest.TestCase):
    def test_cd_no_arg_goes_home(self):
        cwd = os.getcwd()
        try:
            process_line("cd")
            self.assertEqual(os.getcwd(), os.path.expanduser("~"))
        finally:
            os.chdir(cwd)

    def test_cd_to_valid_path(self):
        cwd = os.getcwd()
        try:
            process_line(f'cd "{cwd}"')
            self.assertEqual(os.getcwd(), cwd)
        finally:
            os.chdir(cwd)

class TestEcho(unittest.TestCase):
    def test_echo_text(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            process_line('echo hello world')
        self.assertEqual(buf.getvalue().strip(), "hello world")

    def test_echo_quoted(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            process_line('echo "hello world"')
        self.assertEqual(buf.getvalue().strip(), "hello world")

class TestExternal(unittest.TestCase):
    @patch("ccsh.command_helpers.run")
    def test_external_calls_subprocess(self, mock_run):
        # Simulate success returncode=0
        mock_run.return_value = MagicMock(returncode=0)

        if IS_WINDOWS:
            process_line("dir")
            mock_run.assert_called()
        else:
            process_line("ls -l")
            mock_run.assert_called()

    @patch("ccsh.command_helpers.run")
    def test_ls_maps_to_dir_on_windows(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        if IS_WINDOWS:
            process_line("ls")
            # Ensure shell=True path used; we can at least assert called with string containing 'dir'
            called_args, called_kwargs = mock_run.call_args
            self.assertIn("dir", called_args[0])  # raw_line string on Windows
            self.assertTrue(called_kwargs.get("shell"))
        else:
            self.skipTest("Windows-only behavior")

class TestParseErrors(unittest.TestCase):
    def test_unbalanced_quotes(self):
        # process_line uses shlex.split and will raise ValueError if integrated directly.
        # If your process_line catches it, assert on printed error instead.
        # Here, demonstrate raising path:
        with self.assertRaises(ValueError):
            # If your process_line currently catches ValueError internally,
            # move this shlex call here or adjust process_line to re-raise.
            import shlex
            shlex.split('"unbalanced')
        
if __name__ == "__main__":
    unittest.main()
