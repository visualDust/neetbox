import asyncio
import os
import subprocess
from threading import Thread

from vdtoys.mvc import Singleton

from neetbox.config.project import _get_module_level_config
from neetbox.utils import DaemonableProcess


class ShellAgent(metaclass=Singleton):
    def __init__(self) -> None:
        shell_exec = "cmd.exe" if os.name == "nt" else "/bin/bash"
        self.daemonable = DaemonableProcess(
            command_line=shell_exec,
            redirect_stdin=subprocess.PIPE,
            redirect_stdout=subprocess.PIPE,
            redirect_stderr=subprocess.PIPE,
        )

    def _send_to_ws(self):
        pass

    def _send_to_stdin(self, string, flush=True):
        self.proc.redirect_stdin.write(string.encode())
        if flush:
            self.proc.redirect_stdin.flush()

    async def read_stdout(self):
        while True:
            output = self.proc.stdout.read(1)  # read stdio nonblocking
            if output:
                await self._send_to_ws(output.decode())

    async def start(self, path):
        path = path or os.getcwd()
        self.proc = self.daemonable.start(shell=True, path=path)

        await asyncio.gather(self.read_stdout())


# shell = ShellAgent()

if __name__ == "__main__":
    pass
