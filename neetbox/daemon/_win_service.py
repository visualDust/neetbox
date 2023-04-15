import os
import sys
from os.path import splitext, abspath
from sys import modules

from neetbox.daemon._daemon import daemon_process
from neetbox.logging import logger

from neetbox.utils import pkg
import win32api
import win32event
import win32service
import win32serviceutil
        
class NEETBOXService(win32serviceutil.ServiceFramework):
    _svc_name_ = "NEETBOX"
    _svc_description_ = "NEETBOX daemon service"
    _config = None

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        # redirect stdout and stderr to files for logging
        # the dir of the log files is the dir of the service exe
        # For the conda env, the dir will be like:
        # D:\Softwares\Miniconda3\envs\xxx\Lib\site-packages\win32
        sys.stdout = open(os.path.join(os.getcwd(), "stdout.log"), "a+")
        sys.stderr = open(os.path.join(os.getcwd(), "stderr.log"), "a+")
        self.run = True

    @staticmethod
    def set_config(config):
        NEETBOXService._config = config

    def SvcDoRun(self):
        try:
            daemon_process(self._config)
        except Exception as e:
            logger.err(f"Service {self._svc_name_} failed because {e}.")
            self.SvcStop()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.run = False


def installService(
    cls=NEETBOXService, cfg=None, display_name: str = None, stay_alive: bool = True
):
    cls.set_config(cfg)
    name = cls._svc_name_
    cls._svc_display_name_ = display_name or name
    try:
        module_path = modules[cls.__module__].__file__
    except AttributeError:
        from sys import executable

        module_path = executable
    module_file = splitext(abspath(module_path))[0]
    cls._svc_reg_class_ = "%s.%s" % (module_file, cls.__name__)
    if stay_alive:
        win32api.SetConsoleCtrlHandler(lambda x: True, True)

    # check if the service is already installed
    try:
        win32serviceutil.QueryServiceStatus(cls._svc_name_)
        logger.log(f"Service {name} already installed.")

        # if installed, start it
        win32serviceutil.StartService(cls._svc_name_)
        logger.log(f"Service {name} started successfully.")
        return
    except win32service.error as e:
        pass

    # install and start the service
    try:
        win32serviceutil.InstallService(
            cls._svc_reg_class_,
            cls._svc_name_,
            cls._svc_display_name_,
            startType=win32service.SERVICE_AUTO_START,
        )
        logger.log(f"Service {name} installed successfully.")
        win32serviceutil.StartService(cls._svc_name_)
        logger.log(f"Service {name} started successfully.")
    except Exception as e:
        logger.err(f"Service {name} install failed because {e}.")
        raise


if __name__ == "__main__":
    # just for test
    NEETBOXService.set_config(
        {
            "server": "localhost",
            "port": 20202,
            "enable": True,
        }
    )
    # win32serviceutil.HandleCommandLine(NEETBOXService)
    installService()
