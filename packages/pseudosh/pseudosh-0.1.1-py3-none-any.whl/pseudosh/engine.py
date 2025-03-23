import io
import os
import shlex
import shutil
import sys
from dataclasses import dataclass
from typing import TextIO

from .models import ShellCommandFatalError, ShellExit


@dataclass
class CommandSplit:
    command: str
    concatenate_last_output: bool


class ShellEngine:
    """Shell engine implementing basic Unix commands with input/output redirection and pipes."""

    def __init__(self):
        self.commands = {
            'cat': self.cat,
            'mkdir': self.mkdir,
            'echo': self.echo,
            'pwd': self.pwd,
            'touch': self.touch,
            'rm': self.rm,
            'exit': self.exit,
        }
        self.cursor = os.getcwd()

    def exit(self,
             args: list[str],
             output: TextIO,
             input_stream: TextIO | None = None) -> int:
        raise ShellExit()

    def execute(self, command_str: str) -> int:
        return self.execute_pipeline(command_str)

    def execute_pipeline(self, command_str: str) -> int:
        commands = self._split_commands(command_str)
        if not commands:
            return 0

        previous_output = None
        exit_code = 0

        for i, split in enumerate(commands):
            is_last = i == len(commands) - 1

            current_output = io.StringIO() if not is_last else sys.stdout

            if not split.concatenate_last_output:
                previous_output = None

            exit_code = self.execute_single_command(split.command,
                                                    previous_output,
                                                    current_output)
            if exit_code != 0:
                return exit_code

            if not is_last:
                current_output.seek(0)
                previous_output = current_output
            else:
                previous_output = None

        return exit_code

    @staticmethod
    def _split_commands(s: str) -> list[CommandSplit]:
        parts: list[CommandSplit] = []
        current: list[str] = []
        in_single = False
        in_double = False
        escape = False

        next_is_pipe = False

        for char in s:
            if escape:
                current.append(char)
                escape = False
            elif char == '\\':
                escape = True
                current.append(char)
            elif char == "'" and not in_double:
                in_single = not in_single
                current.append(char)
            elif char == '"' and not in_single:
                in_double = not in_double
                current.append(char)
            elif char == '|' and not (in_single or in_double):
                # parts.append(''.join(current).strip())
                parts.append(
                    CommandSplit(''.join(current).strip(), next_is_pipe))
                next_is_pipe = True
                current = []
            elif char == '&' and not (in_single or in_double):
                # parts.append(''.join(current).strip())
                if current:
                    parts.append(
                        CommandSplit(''.join(current).strip(), next_is_pipe))
                next_is_pipe = False
                current = []
            else:
                current.append(char)
        if current:
            # parts.append(''.join(current).strip())
            parts.append(CommandSplit(''.join(current).strip(), next_is_pipe))
        return parts

    def execute_single_command(self,
                               command_str: str,
                               input_stream: TextIO | None = None,
                               output_stream: TextIO = sys.stdout) -> int:
        try:
            parts = shlex.split(command_str, posix=True)
        except ValueError as e:
            print(f"Syntax error: {e}", file=sys.stderr)
            return 1

        # 处理连写的重定向符号 (如 "123>file.txt")
        processed_parts = []
        for part in parts:
            processed_parts.extend(self.split_redirections(part))
        parts = processed_parts

        stdout_file = None
        stdout_mode = 'w'
        args = []
        i = 0

        while i < len(parts):
            part = parts[i]
            if part in ('>', '>>'):
                if i + 1 >= len(parts):
                    print(f"Syntax error: no file specified for '{part}'",
                          file=sys.stderr)
                    return 1
                stdout_file = parts[i + 1]
                stdout_mode = 'a' if part == '>>' else 'w'
                i += 2
            else:
                args.append(part)
                i += 1

        if not args:
            return 0

        cmd = args[0]
        cmd_args = args[1:]

        if cmd not in self.commands:
            print(f"{cmd}: command not found", file=sys.stderr)
            return 1

        try:
            if stdout_file is not None:
                full_stdout_path = os.path.join(self.cursor, stdout_file)
                with open(full_stdout_path, stdout_mode) as f:
                    return self.commands[cmd](cmd_args, f, input_stream)
            else:
                return self.commands[cmd](cmd_args, output_stream,
                                          input_stream)
        except Exception as e:
            print(f"{cmd}: error - {str(e)}", file=sys.stderr)
            return 1

    def split_redirections(self, s: str) -> list[str]:
        """拆分包含连写重定向符号的参数"""
        parts = []
        current = s
        while True:
            split = self.split_first_redirection(current)
            if len(split) == 1:
                parts.append(current)
                break
            pre, op, post = split
            if pre: parts.append(pre)
            parts.append(op)
            current = post
        return parts

    def split_first_redirection(self, s: str) -> list:
        """找到第一个未被转义或引号包裹的重定向符号"""
        in_quote = None
        escaped = False
        for i, c in enumerate(s):
            if escaped:
                escaped = False
                continue
            if c == '\\':
                escaped = True
                continue
            if c in ('"', "'"):
                if in_quote == c:
                    in_quote = None
                elif not in_quote:
                    in_quote = c
                continue
            if not in_quote and c == '>':
                # 检查是否是双大于号
                if i + 1 < len(s) and s[i + 1] == '>':
                    return [s[:i], '>>', s[i + 2:]]
                return [s[:i], '>', s[i + 1:]]
        return [s]

    def cat(self,
            args: list[str],
            output: TextIO,
            input_stream: TextIO | None = None) -> int:
        line_number = False

        while args and args[0].startswith('-'):
            opt = args.pop(0)
            if opt == '-n':
                line_number = True
            else:
                print(f"cat: invalid option {opt}", file=sys.stderr)
                return 1

        if not args:
            stream = input_stream if input_stream is not None else sys.stdin
            try:
                for i, line in enumerate(stream, start=1):
                    if line_number:
                        output.write(f"{i:6d}\t{line}")
                    else:
                        output.write(line)
            except AttributeError:
                print("cat: input error", file=sys.stderr)
                return 1
            return 0

        for filename in args:
            full_path = os.path.join(self.cursor, filename)
            try:
                with open(full_path, 'r') as f:
                    for i, line in enumerate(f, start=1):
                        if line_number:
                            output.write(f"{i:6d}\t{line}")
                        else:
                            output.write(line)
            except FileNotFoundError:
                print(f"cat: {filename}: No such file or directory",
                      file=sys.stderr)
                return 1
            except IsADirectoryError:
                print(f"cat: {filename}: Is a directory", file=sys.stderr)
                return 1
        return 0

    def mkdir(self,
              args: list[str],
              output: TextIO,
              input_stream: TextIO | None = None) -> int:
        parents = False
        while args and args[0].startswith('-'):
            opt = args.pop(0)
            if opt == '-p':
                parents = True
            else:
                print(f"mkdir: invalid option {opt}", file=sys.stderr)
                return 1

        if not args:
            print("mkdir: missing operand", file=sys.stderr)
            return 1

        for dirname in args:
            full_path = os.path.join(self.cursor, dirname)
            try:
                if parents:
                    os.makedirs(full_path, exist_ok=True)
                else:
                    os.mkdir(full_path)
            except FileExistsError:
                print(
                    f"mkdir: cannot create directory '{dirname}': File exists",
                    file=sys.stderr)
                return 1
            except FileNotFoundError:
                print(
                    f"mkdir: cannot create directory '{dirname}': No parent directory",
                    file=sys.stderr)
                return 1
        return 0

    def echo(self,
             args: list[str],
             output: TextIO,
             input_stream: TextIO | None = None) -> int:
        escape_mode = 'disable'  # Default is -E
        suppress_nl = False
        show_help = False
        show_version = False
        str_args = []

        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '--help':
                show_help = True
                break
            elif arg == '--version':
                show_version = True
                break
            elif arg.startswith('--'):
                print(f"echo: invalid option -- {arg[2:]}", file=sys.stderr)
                return 1
            elif arg.startswith('-') and len(arg) > 1:
                for char in arg[1:]:
                    if char == 'n':
                        suppress_nl = True
                    elif char == 'e':
                        escape_mode = 'enable'
                    elif char == 'E':
                        escape_mode = 'disable'
                    else:
                        print(f"echo: invalid option -- {char}",
                              file=sys.stderr)
                        return 1
                i += 1
            else:
                str_args = args[i:]
                break

        if show_help:
            help_text = """Usage: echo [SHORT-OPTION]... [STRING]...
    or:  echo LONG-OPTION
    Echo the STRING(s) to standard output.

    -n        do not output the trailing newline
    -e        enable interpretation of backslash escapes
    -E        disable interpretation of backslash escapes (default)
        --help     display this help and exit
        --version  output version information and exit

    If -e is in effect, the following sequences are recognized:

    \\\\      backslash
    \\a      alert (BEL)
    \\b      backspace
    \\c      stop output after this
    \\e      escape
    \\f      form feed
    \\n      new line
    \\r      carriage return
    \\t      horizontal tab
    \\v      vertical tab
    \\0NNN   byte with octal value NNN (1 to 3 digits)
    \\xHH    byte with hexadecimal value HH (1 to 2 digits)
    """
            output.write(help_text)
            return 0

        if show_version:
            version_text = """echo (GNU coreutils) 9.5
    Copyright (C) 2024 Free Software Foundation, Inc.
    License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.
    This is free software: you are free to change and redistribute it.
    There is NO WARRANTY, to the extent permitted by law.

    Written by Brian Fox and Chet Ramey.
    """
            output.write(version_text)
            return 0

        # Process string arguments
        enable_escape = (escape_mode == 'enable')
        output_parts = []
        truncate = False

        for s in str_args:
            processed, truncated = self.process_echo_escape(s, enable_escape)
            output_parts.append(processed)
            if truncated:
                truncate = True
                break

        full_output = ' '.join(output_parts)

        if not truncate and not suppress_nl:
            full_output += '\n'

        output.write(full_output)
        return 0

    def process_echo_escape(self, s: str,
                            enable_escape: bool) -> tuple[str, bool]:
        if not enable_escape:
            return s, False

        result = []
        i = 0
        length = len(s)
        truncate = False

        while i < length:
            if s[i] == '\\' and i + 1 < length:
                i += 1  # Skip backslash
                char = s[i]

                # Handle escape sequences
                if char == 'a':
                    result.append('\a')
                elif char == 'b':
                    result.append('\b')
                elif char == 'c':
                    truncate = True
                    break
                elif char == 'e':
                    result.append('\x1B')
                elif char == 'f':
                    result.append('\f')
                elif char == 'n':
                    result.append('\n')
                elif char == 'r':
                    result.append('\r')
                elif char == 't':
                    result.append('\t')
                elif char == 'v':
                    result.append('\v')
                elif char == '\\':
                    result.append('\\')
                elif char == '0':
                    # Octal escape (1-3 digits)
                    max_digits = 3
                    octal_str = ''
                    j = i
                    while j < length and len(
                            octal_str) < max_digits and s[j] in '01234567':
                        octal_str += s[j]
                        j += 1
                    if octal_str:
                        result.append(chr(int(octal_str, 8)))
                        i = j - 1  # Adjust position
                    else:
                        result.append('\0')
                elif char == 'x':
                    # Hexadecimal escape (1-2 digits)
                    hex_str = ''
                    j = i + 1
                    while j < length and len(hex_str) < 2 and s[j].lower(
                    ) in '0123456789abcdef':
                        hex_str += s[j]
                        j += 1
                    if hex_str:
                        result.append(chr(int(hex_str, 16)))
                        i = j - 1
                    else:
                        result.append('\\x')
                else:
                    # Unknown escape, output literal
                    result.append('\\' + char)
            else:
                result.append(s[i])
            i += 1

        return ''.join(result), truncate

    def pwd(self,
            args: list[str],
            output: TextIO,
            input_stream: TextIO | None = None) -> int:
        output.write(f"{self.cursor}\n")
        return 0

    def touch(self,
              args: list[str],
              output: TextIO,
              input_stream: TextIO | None = None) -> int:
        if not args:
            print("touch: missing file operand", file=sys.stderr)
            return 1

        for filename in args:
            full_path = os.path.join(self.cursor, filename)
            try:
                with open(full_path, 'a'):
                    os.utime(full_path, None)
            except FileNotFoundError:
                open(full_path, 'w').close()
            except IsADirectoryError:
                print(f"touch: cannot touch '{filename}': Is a directory",
                      file=sys.stderr)
                return 1
        return 0

    def rm(self,
           args: list[str],
           output: TextIO,
           input_stream: TextIO | None = None) -> int:
        recursive = False
        force = False

        while args and args[0].startswith('-'):
            opt = args.pop(0)
            if opt == '--':
                break
            for char in opt[1:]:
                if char == 'r':
                    recursive = True
                elif char == 'f':
                    force = True
                else:
                    print(f"rm: invalid option -- '{char}'", file=sys.stderr)
                    return 1

        if not args:
            print("rm: missing operand", file=sys.stderr)
            return 1

        exit_code = 0
        for path in args:
            full_path = os.path.join(self.cursor, path)
            try:
                if os.path.isdir(full_path):
                    if recursive:
                        shutil.rmtree(full_path, ignore_errors=force)
                    else:
                        if not force:
                            print(
                                f"rm: cannot remove '{path}': Is a directory",
                                file=sys.stderr)
                            exit_code = 1
                else:
                    os.remove(full_path)
            except FileNotFoundError:
                if not force:
                    print(
                        f"rm: cannot remove '{path}': No such file or directory",
                        file=sys.stderr)
                    exit_code = 1
            except Exception as e:
                if not force:
                    print(f"rm: cannot remove '{path}': {str(e)}",
                          file=sys.stderr)
                    exit_code = 1
        return exit_code


if __name__ == "__main__":
    engine = ShellEngine()
    # Test pipeline
    engine.execute("echo 'Hello World' | cat")
    # Test commands with redirection
    engine.execute("mkdir -p test_dir")
    engine.execute("echo 'Hello World' > test_dir/file.txt")
    engine.execute("cat -n test_dir/file.txt")
    engine.execute("touch test_dir/new_file")
    engine.execute("rm -rf test_dir")
