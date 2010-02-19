"""
    `Heart` Agent
    
    - Responds to the question "beat?"
    
    @author: Jean-Lou Dupont

    Created on 2010-02-18
"""
__all__=[]

from threading import Event, Thread

from phidgetsdbus.mbus import Bus


class IntervalTimer(Thread):
    """ Threading based Interval Timer
    
        This interval timer is better suited than
        using "signal" based one as it doesn't
        generate IOError exceptions (which disrupts
        communications).
    """
    def __init__(self, interval, callable):
        Thread.__init__(self)
        self.interval = interval
        self.callable = callable
        self.finished = Event()
 
    def run(self):
        while not self.finished.is_set():
            self.finished.wait(self.interval)
            if not self.finished.is_set():
                self.callable()
 
    def cancel(self):
        self.finished.set()


class HeartAgent(object):
    
    _INTERVAL=2  ## seconds
    
    def __init__(self):
        self._beat=False
        self._timer=IntervalTimer(self._INTERVAL, self._tick)
        self._timer.start()
    
    def _tick(self):
        """Alarm Signal Handler"""
        self._beat=True ## atomic assignment

    def _qbeat(self):
        Bus.publish(self, "beat", self._beat)
        self._beat=False ## atomic assignment
        
    
_heart=HeartAgent()
Bus.subscribe("beat?", _heart._qbeat)





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

