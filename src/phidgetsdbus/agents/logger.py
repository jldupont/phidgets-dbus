"""
    Logger - Message Bus Agent

    @author: Jean-Lou Dupont

    Created on 2010-02-17
"""
__all__=[]

import os
import multiprocessing
import logging

from phidgetsdbus.mbus import Bus

class _Printer(object):
    def __init__(self, name):
        self.name = name
        
    def log(self, level, msg):
        if self.name:
            print "%s:%s: %s" % (self.name, level, msg)
        else:
            print "%s: %s" % (level, msg)

class Logger(object):
    """
    Simple logging class
    """
    mlevel={"info":     logging.INFO
            ,"warning": logging.WARNING
            ,"error":   logging.ERROR
            }
    
    def __init__(self, appName=None, logPath="/var/log"):
        self._name=appName
        self._path=logPath
        self.fhdlr=None
        
        ## provide a sensible default
        self._logger=_Printer(appName)
    
    def _console(self, *arg):
        if len(arg) == 1:
            print "INFO: %s" % arg
            return
        print "%s: %s" % (arg[0], arg[1])

    def _reset(self, *arg):
        print "logger: reset"
        if self.fhdlr:
            logging.shutdown([self.fhdlr])
        self._logger=None

    def _setup(self):
        print "logger._setup"
        self._logger=multiprocessing.get_logger()
        
        path=os.path.expandvars(os.path.expanduser(self._path))
        self.fhdlr=logging.FileHandler(path)
        
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        self.fhdlr.setFormatter(formatter)
        self._logger.addHandler(self.fhdlr)
        self._logger.setLevel(logging.INFO)
        
        
    def _hlogpath(self, name, path):
        self._path=path
        self._name=name
        self._setup()

    def _hlog(self, *arg):
        if self._logger is None:
            self._setup()
        
        if len(arg) == 1:
            self._logger.log(logging.INFO, arg[0])
        else:
            level=self.mlevel.get(arg[0], logging.INFO)
            self._logger.log(level, arg[1])
    
    def _hshutdown(self, *arg):
        print "shutdown!"
        logging.shutdown([self.fhdlr])
    
    
_log=Logger()
Bus.subscribe("log",           _log._hlog)
Bus.subscribe("logpath",       _log._hlogpath)
Bus.subscribe("shutdown",      _log._hshutdown)
Bus.subscribe("proc_starting", _log._reset)

