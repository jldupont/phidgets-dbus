"""
    @author: Jean-Lou Dupont

    Created on 2010-02-18
"""
__all__=[]

from phidgetsdbus.mbus import Bus


class WatchDogAgent(object):
    
    def __init__(self):
        self.is_child=False
    
    def _hbeat(self, state):
        pass
    
    def _hstarting(self):
        """ Only "child" processes receives this message

            Intercepting this message serves to distinguish
            the Main process from the Child process(es)  
        """
        self.is_child=True
    
    def _hproc(self, pdetails):
        pass
    

    
_watchdog=WatchDogAgent()
Bus.subscribe("beat",          _watchdog._hbeat)
Bus.subscribe("proc",          _watchdog._hproc)
Bus.subscribe("proc_starting", _watchdog._hstarting)
