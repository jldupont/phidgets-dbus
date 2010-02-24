"""
    @author: jldupont

    Created on 2010-02-15
"""
__all__=[]
import sys

def findModObject(mod, objname):
    """ Locates the mod:object for this application
    """
    for mod_name in sys.modules:
        mt=mod_name.split(".")
        while mt: ## longest prefix match
            if mod==mt:  
                return sys.modules[mod_name].__dict__[objname]
            mt.pop(0)
    raise RuntimeError("cannot find module(%s) object name(%s)" % (mod, objname))

Bus=findModObject(["system", "mbus"], "Bus")

#Phidget specific imports
from Phidgets.Devices.InterfaceKit import *  #@UnusedWildImport
from Phidgets.PhidgetException import *      #@UnusedWildImport
from Phidgets.Events.Events import *         #@UnusedWildImport


class IfkAgent(object):
    """
    """
    def __init__(self, serial):
        self.serial=serial
        
        try:
            self.ifk=InterfaceKit()
            self._setHooks()
        except:
            w="Can't instantiate a Phidgets.Devices.InterfaceKit"
            Bus.publish(self, "%log", "warning", w)
            #raise RuntimeError(w)
        
    def _setHooks(self):
        self.ifk.setOnAttachHandler(self._onAttach)
        self.ifk.setOnDetachHandler(self._onDetach)
        self.ifk.setOnErrorHandler(self._onError)
        self.ifk.setOnInputChangedHandler(self._onInputChanged)
        self.ifk.setOnOutputChangedHandler(self._onOutputChanged)
        self.ifk.setOnSensorChangedHandler(self._onSensorChanged)
        
    def _onAttach(self, e):
        pass
    
    def _onDetach(self, e):
        pass
    
    def _onError(self, e):
        pass

    def _onInputChanged(self, e):
        pass
    
    def _onOutputChanged(self, e):
        pass
    
    def _onSensorChanged(self, e):
        pass


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


## =====================================================================    

_ifkManager=IfkManager()
Bus.subscribe("device-attached", _ifkManager._onAttached)
