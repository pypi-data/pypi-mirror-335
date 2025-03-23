import logging
from typing import Optional

from .path import getBaseDir, getCurrentPath

#############################################################################################################

def setLogger(
    name: Optional[str] = None,
    level: int = logging.DEBUG,
    format: Optional[str] = '%(asctime)s - %(levelname)s - %(message)s',
    logPath: str = "%s/myLog.log" % getBaseDir(getCurrentPath()),
):
    """
    Set logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(format)

    consoleHeader = logging.StreamHandler()
    consoleHeader.setFormatter(formatter)
    logger.addHandler(consoleHeader)

    fileHandler = logging.FileHandler(logPath, encoding = 'utf-8')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    return logger

#############################################################################################################