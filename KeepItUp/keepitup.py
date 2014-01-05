import time
from repeatingtimer import RepeatingTimer
from harddrive_enumerator import harddrive_enumerator
import logging
import logging.handlers
from harddrive import HardDrive

INTERVAL_SECS = 3 * 60 #make busy every 3 minutes
REPOLL_INTERVAL_SECS = 60 * 60 #repoll hourly
MAX_LOG_FILESIZE = 5*1024*1024 # 5MB maximal size for the log file.
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
    harddrivesList = []
    pollHarddrives()

    pollingTimer = RepeatingTimer(REPOLL_INTERVAL_SECS, pollHarddrives)
    pollingTimer.daemon = True # No need to wait for this thread.
    pollingTimer.start()
    
    timer = RepeatingTimer(INTERVAL_SECS, wakeup)
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

# Polls all non-fixed hard drives to the global harddrivesList variable
def pollHarddrives():
    global harddrivesList
    logger.debug("Polling fixed hard drives list..")
    harddrivesList = []
    try:
        for name, volName in harddrive_enumerator():
            harddrivesList.append(HardDrive(name))
    except:
        logger.exception("Failed to enumerate hard drives. Current list is: %s", str(harddrivesList))


# Passes on all non-fixed harddrives in the harddrivesList variable and "makes them busy"
def wakeup():
    # Lists are thread-safe
    global harddrivesList
    for hdd in harddrivesList:
        try:
            hdd.make_busy()
        except OSError, e:
            logger.error("Could not make %s busy, OS error: %s",  hdd.hddname, e)
        except:
            logger.exception("Could not make %s busy", hdd.hddname)

if __name__ == "__main__":
    main()