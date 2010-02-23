"""
    @author: jldupont

    Created on 2010-02-15
"""
from Phidgets.PhidgetException import *  #@UnusedWildImport
from Phidgets.Events.Events import *     #@UnusedWildImport
from Phidgets.Phidget import *           #@UnusedWildImport
from Phidgets.Manager import *           #@UnusedWildImport

from phidgetsdbus.system.mbus import Bus

from Queue import Queue, Empty

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
        self._q=Queue()
        try:
            self._mng=Manager()
        except Exception,e:
            Bus.publish(self, "%log", "error", "Can't instantiate Phidgets.Manager (%s)" % e)
            self._mng=None
        
        self._setup()
        
    def _setup(self):
        self._mng.setOnAttachHandler(self._onAttach)
        self._mng.setOnDetachHandler(self._onDetach)
        self._mng.setOnErrorHandler(self._onError)
        
        try:
            self._mng.openManager()
        except Exception,e:
            Bus.publish(self, "%log", "error", "Can't open Phidgets.Manager (%s)" % e)
            
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
            _dic=msg.pop(0)
            
            print "Manager._hpoll: mtype(%s) dic(%s)" % (_mtype, _dic)
            Bus.publish(self, _mtype, _dic)
    
    def _onAttach(self, e):
        details=self._getDeviceDetails(e.device)
        self._q.put(["device-attached", details], block=True)
        
    def _onDetach(self, e):
        details=self._getDeviceDetails(e.device)
        self._q.put(["device-detached", details], block=True)
        
    def _onError(self, e):
        try:
            details=self._getDeviceDetails(e.device)
            self._q.put(["device-error", details], block=True)
        except Exception,e:
            Bus.publish(self, "%log", "error", "exception whilst attempting to report Phidgets.onError (%s)" % e)        
        
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
Bus.subscribe("%poll", _manager._hpoll)
