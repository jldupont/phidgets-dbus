"""
    DBus API
    
    @author: jldupont

    Created on 2010-02-15
"""
__all__=[]

## Might need to relocate these if additional
## DBus handling points are defined
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

import dbus.service

from phidgetsdbus.mbus import Bus


class DBusAPIHandler(dbus.service.Object):
    """
    DBus signals handler
    """
    PATH="/Device"
    
    def __init__(self):
        dbus.service.Object.__init__(self, dbus.SessionBus(), self.PATH)

    @dbus.service.signal(dbus_interface="com.phidgets.Phidgets", signature="a{sv}")
    def Attached(self, dic):
        """Generated when a device is attached to the host"""

    @dbus.service.signal(dbus_interface="com.phidgets.Phidgets", signature="a{sv}")
    def Detached(self, dic):
        """Generated when a device is detached to the host"""

    @dbus.service.signal(dbus_interface="com.phidgets.Phidgets", signature="a{sv}")
    def Error(self, dic):
        """Generated when an error on a device is detected"""

    @dbus.service.signal(dbus_interface="com.phidgets.Phidgets", signature="sii")
    def Din(self, serial, pin, value):
        """Generated when the state of a digital input changes"""

    @dbus.service.signal(dbus_interface="com.phidgets.Phidgets", signature="sii")
    def Dout(self, serial, pin, value):
        """Generated when the state of a digital output changes"""

    @dbus.service.signal(dbus_interface="com.phidgets.Phidgets", signature="sii")
    def Ain(self, serial, pin, value):
        """Generated when the state of an analog input changes"""


    

_handler=DBusAPIHandler()
Bus.subscribe("device-attached", _handler.Attached)
Bus.subscribe("device-detached", _handler.Detached)
Bus.subscribe("device-error",    _handler.Error)
Bus.subscribe("device-din",      _handler.Din)
Bus.subscribe("device-dout",     _handler.Dout)
Bus.subscribe("device-ain",      _handler.Ain)


