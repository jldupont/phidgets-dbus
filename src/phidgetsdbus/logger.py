"""
    Simple logging module
    
    @author: Jean-Lou Dupont
"""
__all__ = ["log",]

import logging

class Logger(object):
    """
    Simple logging class
    """
    def __init__(self, appName=None, logPath="/var/log/"):
        self._name=appName
        self.logPath=logPath
        self._logger=None
    
    def getName(self):
        return self._name
    
    def setName(self, name):
        self._name=name
        self._logger=logging.getLogger(self._name)
        hdlr=logging.FileHandler("%s%s.log" % (self.logPath, self._name))
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self._logger.addHandler(hdlr)
        self._logger.setLevel(logging.INFO)

    name=property(getName, setName, None, "application name")
    
    def __call__(self, *arg):
        if len(arg) == 1:
            self._logger.info(arg[0])
        else:
            lmethod=getattr(self._logger, arg[0], self._logger.info)
            lmethod(arg[1])
    
log=Logger()



if __name__=="__main__":
    log.logPath="/tmp/"
    log.name="testlogger"
    log("info", "test!")
    log("test2!")
