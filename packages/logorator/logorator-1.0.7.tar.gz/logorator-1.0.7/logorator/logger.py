from functools import wraps
from time import perf_counter
import re
import os
import inspect


class Logger:
    SILENT = False
    OUTPUT_FILE = None

    def __init__(self, silent: bool = None, mode: str = "normal", override_function_name: str = None):
        if silent is not None and not isinstance(silent, bool):
            raise TypeError("`silent` must be a boolean or None.")
        self.silent = Logger.SILENT if silent is None else silent

        if mode not in {"normal", "short"}:
            raise ValueError("`mode` must be either 'normal' or 'short'.")
        self.mode = mode

        self.override_function_name = override_function_name

    def eol(self):
        if self.mode == "short":
            return "\t"
        return "\n"

    @staticmethod
    def log(message: str = "", end: str = ""):
        if not isinstance(message, str):
            raise TypeError("`message` must be a string.")
        if not isinstance(end, str):
            raise TypeError("`end` must be a string.")

        try:
            if Logger.OUTPUT_FILE is None:
                print(message, end=end)
            else:
                with open(Logger.OUTPUT_FILE, "a+") as f:
                    sanitized_message = re.sub(r'\033\[[0-9;]*m', "", message)
                    f.write(sanitized_message + end)
        except IOError as e:
            raise IOError(f"Failed to write to the log file: {Logger.OUTPUT_FILE}. Error: {e}")

    def _log_start(self, func_name: str, args: tuple, kwargs: dict, _logorator_async_func=False) -> None:
        if self.silent:
            return
        async_string = "\033[35masync \033[0m" if _logorator_async_func else ""
        Logger.log(message=f"Running {async_string}\033[32m{func_name} \033[0m ", end=self.eol())
        for arg in args:
            Logger.log(message=f"  \33[33m{str(arg)[:1000]}\033[0m", end=self.eol())
        for key in list(kwargs):
            Logger.log(message=f"  {key}: \33[33m{str(kwargs[key])[:1000]}\033[0m", end=self.eol())

    def _log_end(self, func_name: str, duration: str, first_arg=None, _logorator_async_func=False) -> None:
        if self.silent:
            return
        async_string = "\033[35masync \033[0m" if _logorator_async_func else ""
        arg_str = f" \33[33m({str(first_arg)[:100]})\33[0m" if first_arg is not None else ""
        Logger.log(message=f"Finished {async_string}\033[32m{func_name}{arg_str} \033[0m Time elapsed: \033[32m{duration} ms\033[0m", end="\n")

    def __call__(self, func):
        func_name = self.override_function_name or func.__name__

        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start = perf_counter()
                self._log_start(func_name, args, kwargs, _logorator_async_func=True)

                result = await func(*args, **kwargs)

                end = perf_counter()
                duration = '{:,.2f}'.format((end - start) * 1000)
                first_arg = args[0] if args else None
                self._log_end(func_name, duration, first_arg, _logorator_async_func=True)

                return result

            return async_wrapper
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start = perf_counter()
                self._log_start(func_name, args, kwargs)

                result = func(*args, **kwargs)

                end = perf_counter()
                duration = '{:,.2f}'.format((end - start) * 1000)
                first_arg = args[0] if args else None
                self._log_end(func_name, duration, first_arg)

                return result

            return wrapper

    @staticmethod
    def set_silent(silent: bool = True):
        if not isinstance(silent, bool):
            raise TypeError("`silent` must be a boolean.")
        Logger.SILENT = silent

    @staticmethod
    def set_output(filename: str | None = None):
        if filename is not None and not isinstance(filename, str):
            raise TypeError("`filename` must be a string or None.")

        if filename is not None:
            directory = os.path.dirname(filename)
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                except OSError as e:
                    raise OSError(f"Failed to create directory `{directory}` for log file: {e}")

            try:
                with open(filename, "a+") as f:
                    pass
            except IOError as e:
                raise IOError(f"Failed to open log file `{filename}` for writing: {e}")

        Logger.OUTPUT_FILE = filename

    @staticmethod
    def note(note: str = "", mode: str = "normal"):
        if not isinstance(note, str):
            raise TypeError("`note` must be a string.")
        if mode not in {"normal", "short"}:
            raise ValueError("`mode` must be either 'normal' or 'short'.")

        if Logger.SILENT:
            return

        Logger.log(f"\033[34m{note} \033[0m", end=("\t" if mode == "short" else "\n"))