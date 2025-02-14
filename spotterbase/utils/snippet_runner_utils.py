"""Utilities for running documentation snippets

They are used in ``snippet_test.py`` files in the documentation
to run the snippets and ensure they are up-to-date."""

import sys
import tempfile
from pathlib import Path
import subprocess
from typing import Optional


def run_shell_file(shell_file: Path, cwd: Optional[Path] = None) -> str:
    if cwd is None:
        with tempfile.TemporaryDirectory() as tmp:
            return _run_shell_file_actual(shell_file, Path(tmp))
    else:
        return _run_shell_file_actual(shell_file, cwd)


def _run_shell_file_actual(shell_file: Path, cwd: Path) -> str:
    stdouts: list[str] = []

    current_command = ''

    for line in shell_file.read_text().splitlines(keepends=False):
        if line.startswith('#'):
            continue
        if line.startswith('python3 '):
            line = f'{Path(sys.executable)} {line[len("python3 "):]}'
        if line.endswith('\\'):
            current_command += line[:-1]
            continue
        current_command += line
        result = subprocess.run(
            current_command,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=True,
        )

        if result.returncode:
            raise Exception(f'Error running {current_command}: {result.stderr}')

        stdouts.append(result.stdout)

    return '\n'.join(stdouts)


def run_python_file(py_file: Path, cwd: Optional[Path] = None) -> str:
    if cwd is None:
        with tempfile.TemporaryDirectory() as tmp:
            return _run_python_file_actual(py_file, Path(tmp))
    else:
        return _run_python_file_actual(py_file, cwd)


def _run_python_file_actual(py_file: Path, cwd: Path) -> str:
    result = subprocess.run(
        [sys.executable, py_file],
        cwd=cwd,
        capture_output=True,
        text=True,
    )

    if result.returncode:
        raise Exception(f'Error running {py_file}: {result.stderr}')

    return result.stdout
