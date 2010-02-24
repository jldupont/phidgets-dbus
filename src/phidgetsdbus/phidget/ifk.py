"""
    @author: jldupont

    Created on 2010-02-15
"""
__all__=[]

from Queue import Queue, Empty

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
    def __init__(self, queue, serial):
        self.serial=serial
        self._q=queue
        
        try:
            self.ifk=InterfaceKit()
            self._setHooks()
            self.ifk.openPhidget(int(serial))
        except Exception,e:
            print "*** Exception: ",e
            w="Can't instantiate a Phidgets.Devices.InterfaceKit"
            Bus.publish(self, "%log", "warning", w)
            #raise IfkError(w)
                
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
        ## Message meant for the IFK manager
        self._q.put(["%detached", self.serial])
    
    def _onError(self, e):
        self._q.put(["%device-error", self.serial])        

    def _onInputChanged(self, event):
        i,s = self._getIS(event)
        self._q.put(["%device-din", self.serial, i, s])        
    
    def _onOutputChanged(self, event):
        i,s = self._getIS(event)
        self._q.put(["%device-dout", self.serial, i, s])        
    
    def _onSensorChanged(self, event):
        i,s = self._getIS(event)
        self._q.put(["%device-ain", self.serial, i, s])        

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
        self._q=Queue()
        
    def _hpoll(self, *p):
        """ Pull as much messages as
            are available from the queue
        """ 
        while True:
            try:          msg=self._q.get_nowait()
            except Empty: msg=None
            if msg is None:
                break

            _mtype=msg.pop(0)            
            Bus.publish(self, _mtype, *msg)        
        
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
            
            try:    device=IfkAgent(self._q, serial)
            except: device=None
            
            if device:
                self._devices[serial] = details


## =====================================================================    

_ifkManager=IfkManager()
Bus.subscribe("%device",   _ifkManager._hdevice)
Bus.subscribe("%detached", _ifkManager._hdetached)
Bus.subscribe("%poll",     _ifkManager._hpoll)
