"""
    @author: jldupont

    Created on 2010-02-24
"""
import os
import yaml #@UnresolvedImport
from system.mbus import Bus

class ConfigAgent(object):
    
    CONFIG_PATH="~/.phidgetsdbus/"
    CONFIG_FILE="sensors.config"
    
    REFRESH_INTERVAL=10
    
    def __init__(self):
        self.count=self.REFRESH_INTERVAL+1 ## force early processing
        self._path=self.CONFIG_PATH+self.CONFIG_FILE
        self.cpath=os.path.expandvars(os.path.expanduser(self._path))
        self.mtime=None
        self.config={}
        
        ## Notification flags
        self.nConfigPath=False
        self.nConfigFile=False

    def log(self, level, msg):
        Bus.publish(self, "%log", level, msg)
        
    def _hpoll(self, *p):
        self.count=self.count+1
        if self.count > self.REFRESH_INTERVAL:
            self.count=0
            self.doRefresh()

    def doRefresh(self):
        try:    statinfo=os.stat(self.cpath)
        except: statinfo=None
            
        ##  st_mode, st_ino, st_dev, st_nlink, st_uid, 
        ##  st_gid, st_size, st_atime, st_mtime, st_ctime
        if not statinfo:
            if not self.nConfigPath:
                self.nConfigPath=True
                self.log("warning", "Configuration file not found(%s)" % self.cpath)
        return
        
        mtime=statinfo.st_mtime
        if self.mtime != mtime:
            self.mtime = mtime
            self.nConfigPath=False
            self._handleChange()
            
    def _handleChange(self):
        """ Configuration file changed - process it
        """
        try:
            file=os.open(self.cpath)
            contents=file.readlines()
            file.close()
            self.nConfigFile=False
        except Exception,e:
            if not self.nConfigFile:
                self.nConfigFile=True
                self.log("error", "Unable to load configuration file(%s) error(%s)" % (self.cpath, e))
            return
        
        self.processConfigFile(contents)
        
    def processConfigFile(self, contents):
        """ Process the contents of the configuration file """
        try:
            config=yaml.load(contents)
        except Exception,e:
            self.log("error", "Unable to parse configuration file(%s) error(%s)" % (self.cpath, e))
            return
        
        self.config=config
        Bus.publish(self, "%config-sensors", self.config)
        
    
_ca=ConfigAgent()
Bus.subscribe("%poll", _ca._hpoll)
