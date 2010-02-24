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




class SensorsAgent(object):
    """
    """
    def __init__(self):
        pass
    
    def _hDin(self, serial, pin, value):
        pass
    
    def _hDout(self, serial, pin, value):
        pass

    def _hAin(self, serial, pin, value):
        pass

    
_sa=SensorsAgent()
Bus.subscribe("%din",  _sa._hDin)
Bus.subscribe("%dout", _sa._hDout)
Bus.subscribe("%ain",  _sa._hAin)