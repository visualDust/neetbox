# -*- coding: UTF-8 -*
import getpass
import platform
from datetime import datetime, date
from termcolor import colored
from enum import Enum
import six
import re
import os


class Logger:
    def __init__(this, whom, ic=None, color=None):
        this.ic = ""
        this.color = color
        this.ic = ic
        this.whom = whom
        this.log_writer = None
        this.__conditions__ = []

    def add_condition_check(this, callback: bool):
        this.__conditions__.append(callback)
        return this

    def log(
        this,
        message,
        flag=None,
        with_ic=True,
        with_datetime=True,
        with_identifier=True,
        into_file=True,
        into_stdout=True,
    ):
        for cond in this.__conditions__:
            if not cond:
                return
            
        if type(message) is not str:
            message = str(message)

        if into_stdout:
            pre_text_cmd = ""
            pre_text_cmd += flag if flag is not None else ""
            pre_text_cmd += str(datetime.now()) + " > " if with_datetime else ""

        pre_text_txt = ""
        pre_text_txt += flag if flag is not None else ""
        pre_text_txt += str(datetime.now()) + " > " if with_datetime else ""
        icon_str = this.ic.value if type(this.ic) is IconMode else this.ic
        color_str = this.color.value if type(this.color) is ColorMode else this.color
        if with_ic and this.ic is not None:
            if into_stdout:
                pre_text_cmd += (
                    colored(icon_str, color=color_str)
                    if this.color is not None
                    else icon_str
                )
            # if into_file and this.log_writer is not None:
            # pre_text_txt += icon_str
        if with_identifier:
            if into_stdout:
                pre_text_cmd += (
                    colored(str(this.whom) + " > ", color=color_str)
                    if this.color is not None
                    else str(this.whom) + " > "
                )
            if into_file and this.log_writer is not None:
                pre_text_txt += str(this.whom) + " > "
        if into_stdout:
            print(pre_text_cmd + message)
        if into_file and this.log_writer is not None:
            this.log_writer.write(pre_text_txt + message + "\n")
        return this

    def debug(this, info, flag=f"[{colored('δ', 'cyan')}]"):
        this.log(info, flag, into_file=False)

    def err(this, err, flag=f"[{colored('×', 'red')}]"):
        this.log(err, flag, into_file=False)
        this.log(err, flag, into_stdout=False)

    def banner(this, ch="=", length=80):
        this.log(
            ch * length,
            flag=None,
            with_ic=False,
            with_datetime=False,
            with_identifier=False,
        )
        return this

    def log_os_info(this):
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
        this.log(
            message=message,
            flag=None,
            with_ic=False,
            with_datetime=False,
            with_identifier=False,
        )
        return this

    def log_empty_line(this, line_cnt=1):
        this.log(
            message="\n" * line_cnt,
            flag=None,
            with_ic=False,
            with_datetime=False,
            with_identifier=False,
        )
        return this

    def log_txt_file(this, file):
        if isinstance(file, six.string_types):
            file = open(file)
        str = ""
        for line in file.readlines():
            str += line
        this.log(
            message=str,
            flag=None,
            with_ic=False,
            with_datetime=False,
            with_identifier=False,
        )
        return this

    def set_log_dir(this, path, independent=False):
        if os.path.isfile(path):
            raise "Target path is not a directory."
        if not os.path.exists(path):
            static_logger.log("Directory not found, trying to create.")
            os.makedirs(path)
        log_file_name = ""
        if independent:
            log_file_name += this.whom
        log_file_name += str(date.today())
        this.bind_file(os.path.join(path, log_file_name))
        return this

    def bind_file(this, path):
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
        this.log_writer = writers_dict[log_file_identity]
        return this

    def file_bend(this) -> bool:
        return this.log_writer == None


writers_dict = {}
loggers_dict = {}
static_logger = Logger("TheLoggerRoot                ")


def get_logger(whom, ic=None, color=None) -> Logger:
    if whom in loggers_dict:
        return loggers_dict[whom]
    loggers_dict[whom] = Logger(whom, ic, color)
    return loggers_dict[whom]


def validateTitle(title):
    if platform.system().lower() == "windows":
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        new_title = re.sub(rstr, "_", title)  # replace with '_'
        return new_title
    return title


class IconMode(Enum):
    setting = "⚙"
    star_filled = "★"
    star = "☆"
    circle = "○"
    circle_filled = "●"
    telephone_filled = "☎"
    telephone = "☏"
    smile = "☺"
    smile_filled = "☻"
    jap_no = "の"
    sakura_filled = "✿"
    sakura = "❀"
    java = "♨"
    music = "♪"
    block = "▧"
    left = "⇐"
    up = "⇑"
    right = "⇒"
    down = "⇓"
    left_right = "↹"


class ColorMode(Enum):
    grey = "grey"
    red = "red"
    green = "green"
    yellow = "yellow"
    blue = "blue"
    magenta = "magenta"
    cyan = "cyan"
    white = "white"
