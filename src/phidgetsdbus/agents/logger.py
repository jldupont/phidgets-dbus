"""
    @author: jldupont

    Created on 2010-02-17
"""
__all__=[]

import os
import logging

from phidgetsdbus.mbus import Bus

class Logger(object):
    """
    Simple logging class
    """
    def __init__(self, appName=None, logPath="/var/log"):
        self._name=appName
        self._path=logPath
        
        ## provide a sensible default
        self._logger=self._console
    
    def _console(self, *arg):
        if len(arg) == 1:
            print "INFO: %s" % arg
            return
        print "%s: %s" % (arg[0], arg[1])
        
        
    def _hlogpath(self, name, path):
        self._path=path
        self._name=name
        self._logger=logging.getLogger(self._name)
        path=os.path.expandvars(os.path.expanduser(self._path))
        hdlr=logging.FileHandler("%s/%s.log" % (path, self._name))
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self._logger.addHandler(hdlr)
        self._logger.setLevel(logging.INFO)

    def _hlog(self, *arg):
        if len(arg) == 1:
            self._logger.info(arg[0])
        else:
            lmethod=getattr(self._logger, arg[0], self._logger.info)
            lmethod(arg[1])
    
    
    
_log=Logger()
Bus.subscribe("log",     _log._hlog)
Bus.subscribe("logpath", _log._hlogpath)
