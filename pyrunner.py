import re
import subprocess
import uuid
from functools import partial
from pathlib import Path
from subprocess import CompletedProcess
from typing import List, Tuple, Literal

from IPython.terminal.interactiveshell import TerminalInteractiveShell
from IPython.utils.capture import capture_output
from loguru import logger


class InteractivePythonRunner:
    ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    ERROR_DELIMITERS = '-' * 75

    def __init__(self, ipython_dir: Path, raise_error: bool = True):
        self.ipython_dir = str(ipython_dir)
        self.shell: TerminalInteractiveShell = None
        self.raise_error = raise_error

    def run(self, code: str | List[str]) -> Tuple[str, str | None]:

        with capture_output() as capture:
            code = code if isinstance(code, list) else [code]
            for c in code:
                logger.info(f'run code: {c}')
                self.shell.run_cell(c)

        text = self.ANSI_ESCAPE.sub('', capture.stdout)
        if self.ERROR_DELIMITERS in text:
            out, err = text.split(self.ERROR_DELIMITERS)
        else:
            out, err = text, None
        return out, err

    def __enter__(self):
        logger.info('create ipython instance')
        self.shell = TerminalInteractiveShell(ipython_dir=self.ipython_dir)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info('close ipython instance')
        self.shell.run_cell('exit()')
        if exc_type is not None and self.raise_error == 'raise':
            raise exc_val


class PythonRunner:

    def __init__(self, interpreter_path: Path):
        self.interpreter_path = interpreter_path

    def run_script(self, script: Path) -> CompletedProcess:
        args = [str(self.interpreter_path), str(script)]
        return subprocess.run(args, capture_output=True, text=True)


class CondaEnv:
    BASE_CONDA_ENV_PATH = '/Users/lzx/miniconda3/envs/runner'
    BASE_CONDA_ENV_NAME = 'runner'

    def __init__(self, env_name: str = None):
        self.env_name = env_name or uuid.uuid4().hex
        self.py_console: InteractivePythonRunner = None
        self.py_runner: PythonRunner = None

    def run_script(self, script: Path) -> CompletedProcess:
        return self.py_runner.run_script(script)

    def __enter__(self):
        logger.info(f'create new conda env: {self.env_name}')
        args = ['conda', 'create', '--name', self.env_name, '--clone', self.BASE_CONDA_ENV_NAME]
        result = subprocess.run(args, capture_output=True, text=True)
        logger.info(result.stdout)

        args = ['conda', 'run', '--name', self.env_name, 'which', 'python']
        python_path = subprocess.run(args, capture_output=True, text=True).stdout.strip()
        logger.info(f'python_path: {python_path}')
        self.py_runner = PythonRunner(interpreter_path=Path(python_path))
        self.py_console = partial(InteractivePythonRunner, interpreter=Path(python_path).parent)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info(f'remove conda env: {self.env_name}')
        args = ['conda', 'env', 'remove', '--name', self.env_name]
        subprocess.run(args, capture_output=True, text=True)
        return self
