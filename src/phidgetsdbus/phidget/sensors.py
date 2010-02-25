"""
    Sensors

    - Publishes configuration data on DBus
    - Intercept "Din", "Dout", "Ain" DBus signals,
        perform a look-up in the configuration data,
        map the result to "/Sensors/State/Changed"
    
    @author: jldupont

    Created on 2010-02-24
"""
__all__=[]

from system.mbus import Bus


"""
signal sender=:1.273 -> dest=(null destination) serial=36 path=/Device; interface=com.phidgets.Phidgets; member=Din
   string "80860"
   int32 4
   int32 0
signal sender=:1.273 -> dest=(null destination) serial=37 path=/Device; interface=com.phidgets.Phidgets; member=Din
   string "80860"
   int32 4
   int32 1
"""

class SensorsAgent(object):
    """
    """
    def __init__(self):
        self.map={}
        self.config={}
        self.states={}
    
    ## ==================================================
    
    
    def hConfig(self, config):
        self.config=config
        self.states=config.get("states", None) or config.get("States", None)
    
    def hPinMap(self, map):
        self.map=map
        print "hPinMap: ", map
    
    ## ==================================================
    
    def _hDin(self, serial, pin, value):
        print "_hDin: %s, %s, %s" %( serial, pin, value )
        pname, mval=self.domap(serial, pin, value)
        print "_hDin: pname(%s) mval(%s)" % (pname, mval)
        if mval is not None:
            Bus.publish(self, "%state-changed", serial, pname, mval)
    
    def _hDout(self, serial, pin, value):
        pname, mval=self.domap(serial, pin, value)
        if mval is not None:
            Bus.publish(self, "%state-changed", serial, pname, mval)


    def _hAin(self, serial, pin, value):
        pname, mval=self.domap(serial, pin, value)
        if mval is not None:
            Bus.publish(self, "%state-changed", serial, pname, mval)


    ## ==================================================
    def domap(self, serial, pin, value):
        print "domap: %s, %s, %s" % (serial, pin, value)
        pn=self.pmap(serial, pin)
        print "domap, pn: ", pn
        pstates=self.states.get(pn, {})
        mvalue=pstates.get(value, None)
        return (pn, mvalue)
        

    def pmap(self, serial, pin):
        key="%s.%s" % (serial, pin)
        return self.map.get(key, None)
    

    
_sa=SensorsAgent()
Bus.subscribe("%config-sensors", _sa.hConfig)
Bus.subscribe("%pin-map",        _sa.hPinMap)
Bus.subscribe("%din",  _sa._hDin)
Bus.subscribe("%dout", _sa._hDout)
Bus.subscribe("%ain",  _sa._hAin)