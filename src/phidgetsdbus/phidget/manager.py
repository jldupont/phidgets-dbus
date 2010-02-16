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

import glib #@UnresolvedImport

class ManagerAgent(object):
    """
    glib.idle_add : used as precautionary measure
     as I do not fully understand how the threading model
     works under python. Since I have enabled "thread support"
     through both `gobject` and `dbus`, I hope using this will
     be sufficient to integrate async events coming from the
     phidgets side onto the glib main loop thread side.
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
        details=self._getDeviceDetails(e.device)
        def sendSignal(details):
            def wrapper():
                Bus.publish(self, "device-attached", details)
                log("device attached: details: %s" % details)
            return wrapper
        glib.idle_add(sendSignal(details))
        
    def _onDetach(self, e):
        details=self._getDeviceDetails(e.device)
        def sendSignal(details):
            def wrapper():
                Bus.publish(self, "device-detached", details)
                log("device detached: details: %s" % details)
            return wrapper        
        glib.idle_add(sendSignal(details))        
        
    def _onError(self, e):
        try:
            details=self._getDeviceDetails(e.device)
            def sendSignal(details):
                def wrapper():
                    Bus.publish(self, "device-error", details)
                    log("device error: details: %s" % details)
                return wrapper        
            glib.idle_add(sendSignal(details))
        except Exception,e:
            log("error", "exception whilst attempting to report Phidgets.onError (%s)" % e)        
        
        
    def _getDeviceDetails(self, device):
        details={}
        
        ## should at least have serial number
        try:    details["serial"]  = device.getSerialNum()
        except: pass
        
        try:
            details["name"]    = device.getDeviceName()
            details["type"]    = device.getDeviceType()
            details["version"] = device.getDeviceVersion()
            #details["label"]   = device.getDeviceLabel()  # crashes DBus            
        except:
            pass
        
        return details
        
    
_manager=ManagerAgent()
