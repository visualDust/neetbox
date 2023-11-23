import os
import subprocess
import sys
import time
from typing import List, Literal

is_ms_windows = "win32" in sys.platform or "cygwin" in sys.platform


class DaemonableProcess:
    def __init__(
        self,
        *,
        target: str,
        args: List = [],
        mode: Literal["attached", "detached"],
        redirect_stdout=None,
        redirect_stderr=subprocess.STDOUT,
        use_os_spawn_for_daemon=False,
        redirect_stdin=subprocess.DEVNULL,
        env_append=None,
    ):
        self.target = target
        self.__args = args
        self.__mode = mode
        self.__use_os_spawn_for_daemon = use_os_spawn_for_daemon
        self.__stdin = redirect_stdin
        # self.__is_daemon = is_daemon
        # self.__is_detached = is_detached
        self.__redirect_stdout = redirect_stdout
        self.__redirect_stderr = redirect_stderr
        self.__env = dict(os.environ)
        if env_append is not None:
            self.__env.update(env_append)
        # self.__no_new_window = no_new_window

    @property
    def is_daemon(self):
        return self.__mode == "daemon"

    @property
    def mode(self):
        return self.__mode

    # @property
    # def is_detached(self):
    #     return self.__is_detached

    def start(self):
        if self.__use_os_spawn_for_daemon:
            raise NotImplementedError()
        else:
            # use subprocess
            command_line = [sys.executable, "-m", self.target, *self.__args]

            if is_ms_windows:
                # windows + subprocess
                creationflags = {
                    "attached": 0,
                    "shared": 0,
                    "detached": subprocess.CREATE_NO_WINDOW,  # type: ignore (only for windows)
                }[self.__mode]

                popen = subprocess.Popen(
                    command_line,
                    creationflags=creationflags,
                    stdout=self.__redirect_stdout,
                    stderr=self.__redirect_stderr,
                    stdin=self.__stdin,
                    env=self.__env,
                )
                # print(popen)

                # return_code = popen.wait()
                # print('return_code', return_code)
            else:
                # posix + subprocess
                popen = subprocess.Popen(
                    command_line,
                    stdin=self.__stdin,
                    stdout=self.__redirect_stdout,
                    stderr=self.__redirect_stderr,
                    env=self.__env,
                    start_new_session=self.mode == "detached",
                )

                if self.mode == "attached":
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
