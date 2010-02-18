"""
    `Heart` Agent
    
    - Responds to the question "beat?"
    
    @author: Jean-Lou Dupont

    Created on 2010-02-18
"""
__all__=[]

_INTERVAL=2  ## seconds

import signal

from phidgetsdbus.mbus import Bus

class HeartAgent(object):
    """
    """
    def __init__(self):
        self._beat=False
    
    def __call__(self, signum, _):
        """Alarm Signal Handler"""
        self._beat=True ## atomic assignment

    def _qbeat(self):
        Bus.publish(self, "beat", self._beat)
        self._beat=False ## atomic assignment
        
    
_heart=HeartAgent()
Bus.subscribe("beat?", _heart._qbeat)

signal.signal(signal.SIGALRM, _heart)
signal.setitimer(signal.ITIMER_REAL, _INTERVAL, _INTERVAL)





## =====================================================

if __name__=="__main__":
    from time import sleep
    
    Bus.debug=True
    
    class Cb(object):
        def beat(self, state):
            print "state: ",state
        
    _cb=Cb()
        
    Bus.subscribe("beat", _cb.beat)
    
    while True:
        Bus.publish(None, "beat?")
        sleep(0.1)

