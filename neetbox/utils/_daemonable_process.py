# -*- coding: utf-8 -*-
#
# Author: PaperCube aka 张老师
# Github: github.com/PaperCube
# Date:   20230421

import os
import subprocess
import sys
import time
from types import ModuleType
from typing import List, Literal, Union


class DaemonableProcess:
    def __init__(
        self,
        *,
        target: Union[str, ModuleType],
        args: List = [],
        mode: Literal["attached", "detached"],
        redirect_stdout=None,
        redirect_stderr=subprocess.STDOUT,
        use_os_spawn_for_daemon=False,
        redirect_stdin=subprocess.DEVNULL,
        env_append=None,
    ):
        self.target = target
        self.args = args
        self._mode = mode
        self.use_os_spawn_for_daemon = use_os_spawn_for_daemon
        self.redirect_stdin = redirect_stdin
        # self.__is_daemon = is_daemon
        # self.__is_detached = is_detached
        self.redirect_stdout = redirect_stdout
        self.redirect_stderr = redirect_stderr
        self.env = dict(os.environ)
        if env_append is not None:
            self.env.update(env_append)
        # self.__no_new_window = no_new_window

    @property
    def is_daemon(self):
        return self._mode == "daemon"

    @property
    def mode(self):
        return self._mode

    # @property
    # def is_detached(self):
    #     return self.__is_detached

    def start(self, shell=False, path=None):
        if self.use_os_spawn_for_daemon:
            raise NotImplementedError()
        else:
            # use subprocess
            command_line = (
                [sys.executable, "-m", self.target.__name__, *self.args]
                if isinstance(self.target, ModuleType)
                else [self.target, *self.args]
            )
            path = path or os.getcwd()
            is_ms_windows = "win32" in sys.platform or "cygwin" in sys.platform
            if is_ms_windows:
                # windows + subprocess
                creationflags = {
                    "attached": 0,
                    "shared": 0,
                    "detached": subprocess.CREATE_NO_WINDOW,  # type: ignore (only for windows)
                }[self._mode]

                popen = subprocess.Popen(
                    command_line,
                    creationflags=creationflags,
                    stdout=self.redirect_stdout,
                    stderr=self.redirect_stderr,
                    stdin=self.redirect_stdin,
                    env=self.env,
                    cwd=path,
                    shell=shell,
                )
                # print(popen)

                # return_code = popen.wait()
                # print('return_code', return_code)
            else:
                # posix + subprocess
                popen = subprocess.Popen(
                    command_line,
                    stdin=self.redirect_stdin,
                    stdout=self.redirect_stdout,
                    stderr=self.redirect_stderr,
                    env=self.env,
                    start_new_session=self._mode == "detached",
                    cwd=path,
                    shell=shell,
                )

                if self._mode == "attached":
                    import atexit

                    atexit.register(lambda: popen.terminate())

                # print(popen)

            return popen

    def terminate(self):
        pass


def main():
    DaemonableProcess(
        target="ppcdaemontest.daemon_worker",
        args=["1"],
        mode="attached",
    ).start()
    time.sleep(3)


if __name__ == "__main__":
    main()
