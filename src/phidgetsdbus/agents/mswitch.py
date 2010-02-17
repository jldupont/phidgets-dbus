"""
    Message Switch
    
    System Message types:
    - "_sub"  -> ["_sub", $mtype, $proc_name]
    - "_quit" -> ["_quit"]
    
    Other message format:
    [$mtype, ...]
    
    
    @author: Jean-Lou Dupont
    Created on 2010-02-17
"""
__all__=[]

from phidgetsdbus.mbus import Bus

from multiprocessing import Queue

class MessageSwitch(object):
    """
    Message Switch - multiprocessing enabled
    """
    def __init__(self, iq):
        self._iq=iq
        self._subs={}  ## process details
        self._map={}   ## mtype map list
        self._qmap={}  ## proc name -> queue map

    def _log(self, *p):
        Bus.publish(self, "log", *p)

    def process(self):
        """ Processes the message queue
        
            This method needs to be called in
            order for the input queue messages
            to be processed.
        
            @return: False -> _quit received
            @return: True  -> normal 
        """
        result=True
        while result:
            try:    msg=self._iq.get(False)
            except: msg=None
            if msg is None:
                break
        
            result=self._processMsg(msg)
            
        return result
    
    def _hproc(self, procDetails):
        """ Handle "proc" - Message Bus handler
        
            Grab process details in the setup 
            phase of the application
            
            This message shouldn't appear once
            the application is started
        """
        try:    name=procDetails["name"]
        except: 
            self._log("error", "missing `name` entry in `procDetails`")
            return
        
        try:    iq=procDetails["iq"]
        except:
            self._log("error", "missing `iq` entry in `procDetails`")
            return
            
        self._subs[name]=procDetails
        self._qmap[name]=iq
            
    def _qmqueue(self):
        """ 'mqueue' question handler - Message Bus
        """
        Bus.publish("mqueue", self.iq)
        
    ## ===============================================    
    ## ===============================================
        
        
    def _processMsg(self, msg):
        try:    mtype=msg[0]
        except: mtype=None
        
        if not mtype:
            self._log("missing message type")
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
        if not subs:
            self._log("no subscribers for type(%s)" % mtype)
            return True
        
        for proc_name in subs:
            q=self._qmap.get(proc_name, None)
            if q is None:
                self._log("error", "missing 'queue' object for proc(%s)" % proc_name)
                continue
            q.put(msg)
            self._log("queued, type(%s) for proc(%s)" % (mtype, proc_name))
        return True
        
    def _handleSub(self, mtype, msg):
        """Handles subscription from child processes
        
            ["_sub", $mtype, $proc_name]
               0       1         2
        """
        try:    pname=msg[1]
        except: pname=None
        
        if pname is None:
            self._log("sub: `proc_name` missing for mtype(%s)" % mtype)
            return
        
        subs=self._map.get(mtype, [])
        subs.append(pname)
            

## ================================================================

_centralInputQueue=Queue()
_mswitch=MessageSwitch(_centralInputQueue)
        
Bus.subscribe("proc",    _mswitch._hproc)
Bus.subscribe("mqueue?", _mswitch._qmqueue)
