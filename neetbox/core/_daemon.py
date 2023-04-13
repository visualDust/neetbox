import datetime
import time
import daemon
from neetbox.logging import logger
logger = logger("TEST DAEMON").set_log_dir("./abaaba")
 
def main_program():
    while True:
        e = ''
        try:
            logger.log("Whatever")
        except Exception as exc:
            e =exc
        with open('/tmp/echo.txt', 'a') as fh:
            fh.write(f"{e} at {datetime.datetime.now()}\n")
        time.sleep(1)
 
with daemon.DaemonContext():
    main_program()
 
