"""
    @author: jldupont

    Created on 2010-02-15
"""
from phidgetsdbus.mbus import Bus
from phidgetsdbus.logger import log

import glib #@UnresolvedImport

#Phidget specific imports
from Phidgets.Devices.InterfaceKit import *  #@UnusedWildImport
from Phidgets.PhidgetException import *      #@UnusedWildImport
from Phidgets.Events.Events import *         #@UnusedWildImport


class IfkAgent(object):
    """
    """
    def __init__(self, serial):
        self.serial=serial
        self.ifk=InterfaceKit()
            
        self._setHooks()
        self.doAttach()
        
    def _setHooks(self):
        self.ifk.setOnAttachHandler(self._onAttach)
        self.ifk.setOnDetachHandler(self._onDetach)
        self.ifk.setOnErrorHandler(self._onError)
        self.ifk.setOnInputChangedHandler(self._onInputChanged)
        self.ifk.setOnOutputChangedHandler(self._onOutputChanged)
        self.ifk.setOnSensorChangedHandler(self._onSensorChanged)
        
    def _onAttach(self, e):
        def _log():
            log("IFK serial(%s) attached" % self.serial)
        glib.idle_add(_log)
    
    def _onDetach(self, e):
        def _log():
            log("IFK serial(%s) detached" % self.serial)
        glib.idle_add(_log)
    
    def _onError(self, e):
        pass

    def _onInputChanged(self, e):
        pass
    
    def _onOutputChanged(self, e):
        pass
    
    def _onSensorChanged(self, e):
        pass

    def doAttach(self):
        try:
            log("attempting to open serial(%s)" % self.serial)
            self.ifk.openPhidget(self.serial)
            def _log():
                log("IFK serial(%s) opened" % self.serial)
            glib.idle_add(_log)
        except:
            def _log():
                log("error", "Opening IFK serial(%s) failed" % self.serial)
            glib.idle_add(_log)
        

## =====================================================================


class IfkManager(object):
    """
    """
    def __init__(self):
        self._devices={}
        
    def _onAttached(self, details):
        serial=details.get("serial", None)
        type=details.get("type", None)
        if type=="PhidgetInterfaceKit":
            self._handleIfkInstance(serial)
            
    def _handleIfkInstance(self, serial):
        instance=self._devices.get(serial, None)
        if instance is None:
            def _createIfk(serial):
                def wrapper():
                    ifk=IfkAgent(serial)
                    self._devices[serial]=ifk
                    log("ifk instance, serial: %s" % serial)
                return wrapper
            log("here1")
            glib.idle_add(_createIfk())
            log("here2")
        else:
            instance.doAttach()


## =====================================================================    

_ifkManager=IfkManager()
Bus.subscribe("device-attached", _ifkManager._onAttached)
