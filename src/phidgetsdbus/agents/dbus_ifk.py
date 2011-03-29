"""
    'Dbus Ifk' Agent
    
    Receives DBus signals from "com.phidgets.Phidgets" /Device
     
    @author: jldupont
    Created on Jun 28, 2010
"""
import dbus.service
    
#from system.base import AgentThreadedBase
from system import mswitch

__all__=[]

class SignalRx(dbus.service.Object):
    PATH="/Device"
    IFACE="com.phidgets.Phidgets"
    
    def __init__(self):
        dbus.service.Object.__init__(self, dbus.SessionBus(), self.PATH)
        
        dbus.Bus().add_signal_receiver(self.sDin,
                                       signal_name="Din",
                                       dbus_interface=self.IFACE,
                                       bus_name=None,
                                       path="/Device"
                                       )            

        dbus.Bus().add_signal_receiver(self.sDout,
                                       signal_name="Dout",
                                       dbus_interface=self.IFACE,
                                       bus_name=None,
                                       path="/Device"
                                       )            

        dbus.Bus().add_signal_receiver(self.sAin,
                                       signal_name="Ain",
                                       dbus_interface=self.IFACE,
                                       bus_name=None,
                                       path="/Device"
                                       )            

    def sDin(self, serial, pin, value):
        self._pub(serial, pin, value)

    def sDout(self, serial, pin, value):
        self._pub(serial, pin, value)
        
    def sAin(self, serial, pin, value):
        self._pub(serial, pin, value)
        
    def _pub(self, serial, pin, value):
        try:
            mswitch.publish(self.__class__, "sensor", str(serial), int(pin), int(value))
            #print("Sensor: serial(%s) pin(%s) value(%s)" % (serial, pin, value))
        except Exception,e:
            print "!!! Dbus-ifk: exception: %s" % e

_=SignalRx()
