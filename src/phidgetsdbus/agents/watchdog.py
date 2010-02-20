"""
    Watchdog Agent
    
    Message Bus
    ===========
    Publishes:
    - "_ready" : (only Main) destined to Children processes
    
    Subscribes:
    - "proc_starting" : updates the personality of the Watchdog
    - "_started"      : accumulates to generate "_ready"
    - "proc" : accumulate process details
    - "beat" : TBD
    
    @author: Jean-Lou Dupont

    Created on 2010-02-18
"""
__all__=[]

from phidgetsdbus.mbus import Bus


class WatchDogAgent(object):
    
    def __init__(self):
        self.pname=None
        self.is_child=False
        self._procs={}
        self._started=[]
    
    def _hbeat(self, state):
        pass
    
    def hproc_starting(self, (pname, _)):
        """ Only "child" processes receives this message

            Intercepting this message serves to distinguish
            the Main process from the Child process(es)  
        """
        self.is_child=True
        self.pname=pname
    
    def _hproc(self, pdetails):
        try:    pname=pdetails.get("name", None)
        except: pname=None
        
        ## This error would have been caught upstream
        ## Paranoia in action ;-)
        if pname is not None:      
            procDetails=self._procs.get(pname, {})
            procDetails.update(pdetails)
            self._procs[pname]=procDetails
        
    def _hstarted(self, pname):
        """ Generates `ready` message when all the
            Child processes report as being started
        """
        if not self.is_child:
            self._started.extend([pname])
            if len(self._started) == len(self._procs):
                Bus.publish(self, "_ready")
                    
## ============================================================================
## ============================================================================
    
_watchdog=WatchDogAgent()
Bus.subscribe("beat",          _watchdog._hbeat)
Bus.subscribe("proc",          _watchdog._hproc)
Bus.subscribe("proc_starting", _watchdog._hproc_starting)
Bus.subscribe("started",       _watchdog._hstarted)
