"""
    @author: jldupont

    Created on 2010-02-16
"""
__all__=[]

from multiprocessing import Queue

from phidgetsdbus.mbus import Bus

class MessageSwitch(object):
    """
    Message Switch - multiprocessing enabled
    """
    def __init__(self, iq):
        self._iq=iq
        self._subs={}

    def log(self, *p):
        Bus.publish(self, "log", *p)

    def run(self):
        self.log("Starting")
        
        result=True
        while result:
            msg=self._iq.get()
            result=self.processMsg(msg)
        
    def processMsg(self, msg):
        try:    mtype=msg[0]
        except: mtype=None
        
        if not mtype:
            self.log("missing message type")
            return True
        
        if mtype=="_sub":
            self._handleSub(mtype, msg)
            return True
        
        if mtype=="_quit":
            return False
        
        return self._handleMsg(mtype, msg)
        
    def _handleMsg(self, mtype, msg):
        """Performs message dispatching
        """
        subs=self._subs.get(mtype, [])
        if subs:
            for sub in subs:
                sub.put(msg)
                self.log("queued, type(%s)" % mtype)
        else:
            self.log("no subscribers for type(%s)" % mtype)
        return True
        
    def _handleSub(self, mtype, msg):
        """Handles subscription from child processes
        """
        try:    oq=msg[1]
        except: oq=None
        
        if oq is None:
            self.log("sub: oq missing")
            return
        
        subs=self._subs.get(mtype, [])
        subs.append(oq)
        self._subs[mtype]=subs
            

_centralInputQueue=Queue()
_mswitch=MessageSwitch(_centralInputQueue)
        
