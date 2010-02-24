"""
    @author: jldupont

    Created on 2010-02-15
"""
__all__=[]

from system.mbus import Bus

#Phidget specific imports
from Phidgets.Devices.InterfaceKit import *  #@UnusedWildImport
from Phidgets.PhidgetException import *      #@UnusedWildImport
from Phidgets.Events.Events import *         #@UnusedWildImport

class IfkError(Exception):
    """InterfaceKit related error class"""


class IfkAgent(object):
    """
    """
    def __init__(self, serial):
        self.serial=serial
        
        try:
            self.ifk=InterfaceKit()
            self._setHooks()
            self.ifk.openPhidget(int(serial))
        except Exception,e:
            print "*** Exception: ",e
            w="Can't instantiate a Phidgets.Devices.InterfaceKit"
            Bus.publish(self, "%log", "warning", w)
            raise IfkError(w)
        
    def _setHooks(self):
        self.ifk.setOnAttachHandler(self._onAttach)
        self.ifk.setOnDetachHandler(self._onDetach)
        self.ifk.setOnErrorhandler(self._onError)
        self.ifk.setOnInputChangeHandler(self._onInputChanged)
        self.ifk.setOnOutputChangeHandler(self._onOutputChanged)
        self.ifk.setOnSensorChangeHandler(self._onSensorChanged)
        
    def _onAttach(self, e):
        pass
    
    def _onDetach(self, e):
        Bus.publish(self, "%detached", self.serial)
    
    def _onError(self, e):
        pass

    def _onInputChanged(self, event):
        i,s = self._getIS(event)
        print i,s
    
    def _onOutputChanged(self, e):
        pass
    
    def _onSensorChanged(self, e):
        pass

    def _getIS(self, event):
        return (event.index, event.state)

## =====================================================================


class IfkManager(object):
    """
    Registers the IFK devices
    
    - Generates "%attached" when a new devices is discovered
    - Listens for "%detached"
    """
    def __init__(self):
        self._devices={}
        
    def _hdetached(self, serial):
        try:    del self._devices[serial]
        except:
            Bus.publish(self, "%log", "warning", 
                        "Cannot find previsouly registered device, serial(%s)" % serial)
        
    def _hdevice(self, details):
        """ %device - local message handler
        """
        dtype=details.get("type", None)
        if dtype!="PhidgetInterfaceKit":
            return
            
        serial=details.get("serial", None)
        entry=self._devices.get(serial, {})
        if not entry:
            Bus.publish(self, "%log", "Found IFK device, serial(%s)" % serial)
            Bus.publish(self, "%attached", details)
            
            try:    device=IfkAgent(serial)
            except: device=None
            
            if device:
                self._devices[serial] = details


## =====================================================================    

_ifkManager=IfkManager()
Bus.subscribe("%device",   _ifkManager._hdevice)
Bus.subscribe("%detached", _ifkManager._hdetached)
