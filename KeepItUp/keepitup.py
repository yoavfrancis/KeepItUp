import time
from repeatingtimer import RepeatingTimer
from harddrive_enumerator import harddrive_enumerator
import logging
import logging.handlers
from harddrive import HardDrive

INTERVAL_SECS = 90.0
MAX_LOG_FILESIZE = 5*1024*1024 #5MB
LOG_FILENAME = "keepitup.log"

logger = logging.getLogger("keepitup")

def main():

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=MAX_LOG_FILESIZE)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%m/%d/%Y %I:%M:%S %p')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info("KeepItUp started")

    # Hard drives are only enumerated on the first run of the program.
    harddrives = []
    for name, volName in harddrive_enumerator():
        harddrives.append(HardDrive(name))

    timer = RepeatingTimer(INTERVAL_SECS, wakeup, [harddrives])
    timer.trigger()
    timer.start()
    while timer.isAlive():
        try:
            timer.join(1)
        except KeyboardInterrupt:
            logger.error("Ctrl-C received")
            timer.cancel()
            timer.join()

    logger.info("KeepItUp stopped")

def wakeup(harddrivesList):
    for hdd in harddrivesList:
        try:
            hdd.make_busy()
        except OSError, e:
            logger.error("Could not make %s busy, OS error: %s",  hdd.hddname, e)
        except:
            logger.exception("Could not make %s busy", hdd.hddname)

if __name__ == "__main__":
    main()