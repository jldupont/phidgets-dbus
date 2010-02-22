"""
    Watchdog Agent
    
    Child behavior:
    - receives "beat" message-type & counts them
        - when missing MISSING_BEATS, generate "%bark"
        
    
    Message Bus
    ===========
    Publishes:
    - "%bark"    : error detected
    - "_sigterm" : the process received the SIGTERM signal
    - "_ready"   : (only Main) destined to Children processes
    
    Subscribes:
    - "proc_starting" : updates the personality of the Watchdog
    - "_started"      : accumulates to generate "_ready"
    - "proc"  : accumulate process details
    - "beat"  : from Main process
    - "%beat" : local `heart` beat
    
    @author: Jean-Lou Dupont

    Created on 2010-02-18
"""
__all__=[]
import signal
from phidgetsdbus.mbus import Bus

class WatchDogAgent(object):
    
    MISSING_BEATS = 3
    
    def __init__(self):
        self.pname="__main__"
        self.is_child=False
        self._procs={}
        self._started=[]
        self._term=False
        self._termSent=False
        self._beat_count=0
        signal.signal(signal.SIGTERM, self._sterm)

    def _sterm(self, signum, _):
        """ TERM signal handler"""
        print "*** Watchdog._sterm"
        self._term=True
    
    def _hlbeat(self, *pa):
        """ Local "beat" message-type
        
            Trigger the "" message when enough
            "missing beats" are detected
        """
        ### accumulate "beat" count from main process
        if self.is_child:
            self._beat_count=self._beat_count+1
        
        if self.is_child:
            if self._beat_count >= self.MISSING_BEATS:
                print ">>> BARK! (%s)" % self.pname
                Bus.publish(self, "log", "watchdog expired, proc(%s)" % self.pname)
                Bus.publish(self, "%bark")
    
    def _hbeat(self, *pa):
        """ "Beat" message-type
        
            Incoming from the Main process
        """
        ### reset "watchdog" when a "beat" message
        ### is received from the Main process
        if self.is_child:
            self._beat_count=0
        
        if self._termSent:
            return

        if self._term:
            self._termSent=True
            Bus.publish(self, "log", "SIGTERM received, proc(%s)" % self.pname)
            Bus.publish(self, "_sigterm")
    
    def _hproc_starting(self, (pname, _)):
        """ Only "child" processes receives this message

            Intercepting this message serves to distinguish
            the Main process from the Child process(es)  
        """
        self._beat_count=0
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
Bus.subscribe("%beat",         _watchdog._hlbeat)
Bus.subscribe("beat",          _watchdog._hbeat)
Bus.subscribe("proc",          _watchdog._hproc)
Bus.subscribe("proc_starting", _watchdog._hproc_starting)
Bus.subscribe("started",       _watchdog._hstarted)
