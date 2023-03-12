# -*- coding: UTF-8 -*
import getpass
import inspect
import os, re
import platform
import warnings
from datetime import date, datetime
from enum import Enum
from colorama import Fore
from random import random


def _colored(text, color):
    """_summary_

    Args:
        text (str): original raw string
        color (str | ColorMode): which color

    Raises: Nothing

    Returns:
        str: colored string
    """
    if "ANSI_COLORS_DISABLED" in os.environ or "NO_COLOR" in os.environ:
        warnings.warn(
            "Current environment not supported colored text, please notice that! "
        )

    if hasattr(Fore, color.upper()):
        text = getattr(Fore, color.upper()) + text + Fore.RESET
    else:
        raise ValueError("Wrong color was inputed in colored func.")
    return text


class _Logger:
    def __init__(self, whom=None, icon=None, color=None):
        """Not for ordinary users. Use neetbox.logger.get_logger instead.

        Args:
            whom (any, optional): who owns the logger. Keep it None if you want the logger to auto trace the owner. Defaults to None.
            icon (str, optional): Post a useless icon ahead. Defaults to None.
            color (_type_, optional): Set a color, keep it None to get a random color. Defaults to None.
        """
        if whom is not None:
            self.whom = str(whom)
        else:
            self.whom = _get_caller_identity_()
        if not color:
            color_builtin = ["red", "blue", "yellow", "cyan", "magenta"]
            color = color_builtin[int(random() * len(color_builtin))]
        self.color = color
        self.icon = icon
        self.log_writer = None
        self.__conditions__ = []

    def add_condition_check(self, callback: bool) -> None:
        """Add a condition that logger should check before performing a log

        Args:
            callback (bool): A callback that returns a bool

        Returns: Nothing
        """
        self.__conditions__.append(callback)
        return self

    def log(
        self,
        message,
        flag=None,
        with_ic=True,
        date_time_fmt="%Y-%m-%d-%H:%M:%S",
        with_identifier=True,
        method_level=True,
        into_file=True,
        into_stdout=True,
    ):
        for cond in self.__conditions__:
            if not cond:
                return

        if type(message) is not str:
            message = str(message)

        if into_stdout:
            pre_text_cmd = ""
            pre_text_cmd += flag if flag is not None else ""
            pre_text_cmd += (
                str(datetime.now().strftime(date_time_fmt)) + " > "
                if date_time_fmt
                else ""
            )

        pre_text_txt = ""
        pre_text_txt += flag if flag is not None else ""
        if date_time_fmt:
            pre_text_txt += str(datetime.now().strftime(date_time_fmt)) + " > "
        icon_str = self.icon
        color_str = (
            self.color.value if isinstance(self.color, ColorMode) else self.color
        )
        if with_ic and self.icon is not None:
            if into_stdout:
                pre_text_cmd += (
                    _colored(icon_str, color=color_str)
                    if self.color is not None
                    else icon_str
                )
            # if into_file and self.log_writer is not None:
            # pre_text_txt += icon_str

        """
        Tracing identifier
        """
        if with_identifier:
            whom_str = self.whom
            method_name = ""
            if method_level:
                curframe = inspect.currentframe()
                calframe = inspect.getouterframes(curframe, 2)
                method_name = str(calframe[1][3])
                if method_name == "<module>":
                    method_name = ""
            if whom_str.endswith(".py"):
                sub_caller = _get_caller_identity_()
                if sub_caller == whom_str:
                    sub_caller = ""
                else:
                    sub_caller += " > "
                whom_str += " > " + method_name + " > " * (len(method_name) > 0)
            else:
                whom_str += " > "

            if into_stdout:
                pre_text_cmd += (
                    _colored(text=whom_str, color=color_str)
                    if self.color is not None
                    else whom_str
                )
            if into_file and self.log_writer is not None:
                pre_text_txt += whom_str

        if into_stdout:
            print(pre_text_cmd + message)
        if into_file and self.log_writer is not None:
            self.log_writer.write(pre_text_txt + message + "\n")
        return self

    def debug(self, info, flag=f"[{_colored('δ', 'cyan')}]"):
        self.log(info, flag, into_file=False)
        self.log(info, flag="DEBUG", into_stdout=False)

    def err(self, err, flag=f"[{_colored('×', 'red')}]"):
        self.log(err, flag, into_file=False)
        self.log(err, flag="ERROR", into_stdout=False)

    def log_os_info(self):
        """Log some maybe-useful os info

        Returns:
            _Logger : the logger instance itself
        """
        message = (
            f"whom\t\t|\t" + getpass.getuser() + " using " + str(platform.node()) + "\n"
        )
        message += (
            "machine\t\t|\t"
            + str(platform.machine())
            + " on "
            + str(platform.processor())
            + "\n"
        )
        message += (
            "system\t\t|\t" + str(platform.system()) + str(platform.version()) + "\n"
        )
        message += (
            "python\t\t|\t"
            + str(platform.python_build())
            + ", ver "
            + platform.python_version()
            + "\n"
        )
        self.log(
            message=message,
            with_identifier=False,
            flag=None,
            with_ic=False,
            date_time_fmt=False,
            method_level=False,
        )
        return self

    def skip_lines(self, line_cnt=1):
        """Let the logger log some empty lines

        Args:
            line_cnt (int, optional): how many empty line. Defaults to 1.

        Returns:
            _Logger : the logger instance itself
        """
        self.log(
            message="\n" * line_cnt,
            flag=None,
            with_ic=False,
            date_time_fmt=False,
            method_level=False,
        )
        return self

    def log_txt_file(self, file):
        if isinstance(file, str):
            file = open(file)
        context = ""
        for line in file.readlines():
            context += line
        self.log(
            message=context,
            flag=None,
            with_identifier=False,
            with_ic=False,
            date_time_fmt=False,
            method_level=False,
        )
        return self

    def set_log_dir(self, path, independent=False):
        if os.path.isfile(path):
            raise "Target path is not a directory."
        if not os.path.exists(path):
            static_logger.log(f"Directory {path} not found, trying to create.")
            try:
                os.makedirs(path)
            except:
                static_logger.log(f"Failed when trying to create directory {path}")
                raise Exception(f"Failed when trying to create directory {path}")
        log_file_name = ""
        if independent:
            log_file_name += self.whom
        log_file_name += str(date.today()) + ".log"
        self.bind_file(os.path.join(path, log_file_name))
        return self

    def bind_file(self, path):
        log_file_identity = os.path.abspath(path)
        if os.path.isdir(log_file_identity):
            raise Exception("Target path is not a file.")
        filename = validateTitle(os.path.basename(path))
        dirname = os.path.dirname(path) if len(os.path.dirname(path)) != 0 else "."
        if not os.path.exists(dirname):
            raise Exception(f"Could not find dictionary {dirname}")
        real_path = os.path.join(dirname, filename)
        if log_file_identity not in writers_dict:
            writers_dict[log_file_identity] = open(real_path, "a", buffering=1)
        self.log_writer = writers_dict[log_file_identity]
        return self

    def file_bend(self) -> bool:
        return self.log_writer == None


writers_dict = {}
loggers_dict = {}
static_logger = _Logger(whom="LOGGER")


def get_logger(whom=None, icon=None, color=None, traceback=1) -> _Logger:
    """Get a Logger instance

    Args:
        whom (any, optional): who owns the logger. Keep it None if you want the logger to auto trace the owner. Defaults to None.
        icon (str, optional): Post a useless icon ahead. Defaults to None.
        color (_type_, optional): Set a color, keep it None to get a random color. Defaults to None.

    Returns:
        _Logger: a logger instance
    """
    if whom is None:
        whom = _get_caller_identity_(traceback)
    if whom in loggers_dict:
        return loggers_dict[whom]
    loggers_dict[whom] = _Logger(whom=whom, icon=icon, color=color)
    return loggers_dict[whom]


def _get_caller_identity_(traceback=1):
    whom = None
    stack = inspect.stack()[2][0]
    if "self" in stack.f_locals:
        the_class = stack.f_locals["self"].__class__.__name__
        whom = str(the_class)
    else:
        the_method = stack.f_code.co_name
        previous_frame = inspect.currentframe()
        for i in range(traceback + 1):
            previous_frame = previous_frame.f_back
        (filename, line_number, function_name, lines, index) = inspect.getframeinfo(
            previous_frame
        )
        the_method = filename.split("\\")[-1].split("/")[-1]
        whom = str(the_method)
    return whom


def validateTitle(text: str):
    """Remove invalid characters for windows file systems

    Args:
        title (str): the given title

    Returns:
        str: valid text
    """
    if platform.system().lower() == "windows":
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        new_title = re.sub(rstr, "_", text)  # replace with '_'
        return new_title
    return text


class ColorMode(Enum):
    grey = "grey"
    red = "red"
    green = "green"
    yellow = "yellow"
    blue = "blue"
    magenta = "magenta"
    cyan = "cyan"
    white = "white"
