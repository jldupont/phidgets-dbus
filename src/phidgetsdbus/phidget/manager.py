"""
    @author: jldupont

    Created on 2010-02-15
"""
from Phidgets.PhidgetException import *  #@UnusedWildImport
from Phidgets.Events.Events import *     #@UnusedWildImport
from Phidgets.Phidget import *           #@UnusedWildImport
from Phidgets.Manager import *           #@UnusedWildImport

from phidgetsdbus.mbus import Bus
from phidgetsdbus.logger import log


class ManagerAgent(object):
    """
    """
    def __init__(self):
        try:
            self._mng=Manager()
        except Exception,e:
            log("error", "Can't instantiate Phidgets.Manager (%s)" % e)
            self._mng=None
        
        self._setup()
        
    def _setup(self):
        self._mng.setOnAttachHandler(self._onAttach)
        self._mng.setOnDetachHandler(self._onDetach)
        self._mng.setOnErrorHandler(self._onError)
        
        try:
            self._mng.openManager()
        except Exception,e:
            log("error", "Can't open Phidgets.Manager (%s)" % e)
            
    
    def _onAttach(self, e):
        device=e.device
        details=self._getDeviceDetails(device)
        Bus.publish(self, "device-attached", details)
        log("device attached! details: %s" % details)
        
    def _onDetach(self, e):
        device=e.device
        details=self._getDeviceDetails(device)
        Bus.publish(self, "device-detached", details)
        log("device detached!")
        
    def _onError(self, e):
        pass
        #device=e.device
        
        
    def _getDeviceDetails(self, device):
        details={}
        try:
            details["serial"]  = device.getSerialNum()
            details["name"]    = device.getDeviceName()
            #details["label"]   = device.getDeviceLabel()
            details["type"]    = device.getDeviceType()
            details["version"] = device.getDeviceVersion()
        except:
            pass
        
        return details
        
    
_manager=ManagerAgent()
