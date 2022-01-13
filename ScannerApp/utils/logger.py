import logging 
from logging.handlers import RotatingFileHandler
from pathlib import Path  
import os

def createFolder(folder):
    "create path if not exist"
    _folder = Path(__file__).parent.parent/ folder
    if not os.path.exists(_folder):
        os.mkdir(_folder) 
    return _folder

def createFileHandler(logfileName):
    "create a file handler for logger"
    folder = createFolder('logs')
    fh = RotatingFileHandler( folder / logfileName, maxBytes=2**23, backupCount=10)
    # fh.setLevel(level)
    fh.setFormatter(logging.Formatter(
        '%(asctime)s|%(name)-11s|%(levelname)-8s: %(message)s', datefmt='%m/%d %H:%M:%S'
    ))
    return fh

class Logger():
    def debug(self, x): return 0
    def info(self, x): return 0
    def warning(self, x): return 0
    def error(self, x): return 0
    def critical(self, x): return 0

    def __init__(self,name, logLevel='INFO',fileHandler=None, **kwargs):
        """
        name: the name appended to the begining of each log entry. better less than 11 characters for best alignment.
        fileHandler: the fileHandler to write all the logs.
        """
        self.LOG_LEVEL = logLevel
        self._init_logger(name,fileHandler,logLevel)
    
    def _init_logger(self,name,fileHandler,LOG_LEVEL):
        level = getattr(logging, LOG_LEVEL.upper(), 20)
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.addHandler(fileHandler)
        logger.setLevel(level)
                
        _log_level = ['debug', 'info', 'warning', 'error', 'critical']
        
        for i in _log_level:
            setattr(self, i, getattr(logger, i))



class MyLogger():
    def debug(self, x): return 0
    def info(self, x): return 0
    def warning(self, x): return 0
    def error(self, x): return 0
    def critical(self, x): return 0
    def __init__(self, filename, logLevel, **kwargs):
        self.LOGLEVEL = logLevel
        fh = RotatingFileHandler( filename, maxBytes=2**23, backupCount=10)
        fh.setFormatter(logging.Formatter(
            '%(asctime)s|%(name)-11s|%(levelname)-8s: %(message)s', datefmt='%m/%d %H:%M:%S'
        ))
        self.fh = fh
    
    def get(self,name):
        level = getattr(logging,self.LOGLEVEL.upper(),20)
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.addHandler(self.fh)
        logger.setLevel(level)
        _log_level = ['debug', 'info', 'warning', 'error', 'critical']
        
        for i in _log_level:
            setattr(self, i, getattr(logger, i))



        