import asyncio
import os
import subprocess
from threading import Thread

from neetbox.config import get_module_level_config
from neetbox.utils.mvc import Singleton


class ShellAgent(metaclass=Singleton):
    def __init__(self, path=None) -> None:
        path = path or os.getcwd()
        config = config or get_module_level_config()
        if os.name == "nt":  # running on windows
            shell_exec = "cmd.exe"
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
        else:  # not running on windows
            shell_exec = "/bin/bash"
            creationflags = 0
        self.proc = subprocess.Popen(
            shell_exec,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            creationflags=creationflags,
        )

    def _send_to_ws(self):
        pass

    def _send_to_stdin(self, string, flush=True):
        self.proc.stdin.write(string.encode())
        if flush:
            self.proc.stdin.flush()

    async def read_stdout(self):
        while True:
            output = self.proc.stdout.read(1)  # read stdio nonblocking
            if output:
                await self._send_to_ws(output.decode())


# shell = ShellAgent()
