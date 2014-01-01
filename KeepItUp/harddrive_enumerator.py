import win32api
import os
import sys
import subprocess
import logging
from itertools import izip_longest

#itertools recipe
def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

def harddrive_enumerator():
    """
    Generator to get all (fixed) drive letters in the computers
    Returns tuples of (DriveName, VolumeName) - eg. ("D:", "Samsung Station")
    """
    logger = logging.getLogger("keepitup")
    drivesDetailedList = []
    if sys.platform == "win32":
        logger.debug("Enumerating win32 hard drives")
        getDrivesProc = subprocess.Popen('wmic logicaldisk where drivetype=3 get name, VolumeName /format:list',
                                         shell=True,
                                         stdout=subprocess.PIPE)
        output, err = getDrivesProc.communicate()
        logger.debug("Enumerated hard drives output: %s", output)
        drivesDetailedList = output.split(os.linesep)
    elif sys.platform in ["linux2", "darwin"]:
        logger.debug("Enumerating linux/osx hard drives")
        raise NotImplementedError()
    else:
        logger.error("Cannot enumeratre hard drives - unrecognized OS: %s", sys.platform)
        raise NotImplementedError()
    for name, volumeName in grouper(2, drivesDetailedList):
        if "Name=" in name and "VolumeName" in volumeName:
            name = name[len("Name="):].strip()
            volumeName = volumeName[len("VolumeName="):].strip()
            yield name, volumeName


