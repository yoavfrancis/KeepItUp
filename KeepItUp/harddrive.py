import logging
import os
from tempfile import TemporaryFile

class HardDrive(object):
    """
    Represents a hard drive that we would like to "keep awake".
    This is done by creating (and flushing) a file with random data to the disk.
    """
    FILE_PREFIX = "keepitup_"
    FILE_SIZE = 10*1024 # 10KB

    def __init__(self, hddName):
        self.hddname, _ = os.path.splitdrive(hddName)
        self.logger = logging.getLogger("keepitup")

    def make_busy(self):
        with TemporaryFile(bufsize=0, prefix=HardDrive.FILE_PREFIX, dir=self.hddname) as tmpFile:
            self.logger.debug("Creating temporary file: %s with size: %d", tmpFile.name, HardDrive.FILE_SIZE)
            tmpFile.write(os.urandom(HardDrive.FILE_SIZE))
            tmpFile.flush()
            os.fsync(tmpFile.fileno())



