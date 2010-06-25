"""
    Message Switch
    
    System Message types:
    - "_sub"  -> ["_sub", $mtype, $proc_name]
    - "_quit" -> ["_quit"]
    
    Subscribes
    ==========
    - "mqueue?" : mainly for `Pman` agent in order to deliver to
                  the forked child processes as back channel for
                  communications
                  
    - "mswitch_pump"   : execution slot for processing messages
    - "mswitch_params" : for configuring the switch
    
    Publishes
    =========
    - "mqueue"
    - "log"
    
    Other message format:
    [$mtype, ...]
    
    
    @author: Jean-Lou Dupont
    Created on 2010-02-17
"""
__all__=[]

from phidgetsdbus.mbus import Bus

from Queue import Empty, Full
from multiprocessing import Queue

class MessageSwitch(object):
    """
    Message Switch - multiprocessing enabled
    """
    def __init__(self, mq):
        self._mq=mq
        self._name=None
        self.block=True
        self.timeout=0.1
        
        self._subs={}
        self._qmap={}
        self._child=False
        self._reset()
        
        self._iq=None  ## when instance is in a Child process

    def _reset(self):
        """ Only subscription map needs to
            be reset when transitioning to
            a forked Child
        """
        self._map={}   ## mtype map list        
        #self._subs={}  ## process details
        #self._qmap={}  ## proc name -> queue map


    def _log(self, *p):
        print p
        Bus.publish(self, "log", *p)

    def process(self, block=True, timeout=0.100):
        """ Processes the message queue
        
            This method needs to be called in
            order for the input queue messages
            to be processed. Processes each
            available message in queue and returns
            upon first "None available" condition.
        
            @return: False -> _quit received
            @return: True  -> normal 
            @raise:  EOFError
        """
        result=True
        while result:
            try:    
                if self._child:
                    msg=self._iq.get(block, timeout)
                else:
                    msg=self._mq.get(block, timeout)

            except Empty: msg=None
            except Full:  msg=None
            if msg is None:
                break
        
            result=self._processMsg(msg)
            
        return result
    
    def _hsub(self, msgType):
        """ A "user" of the message bus
            subscribed to a "message type"
        """
    
    def _hstart(self):
        """ The Child forking process is about to begin
        """
    
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
        Bus.publish(self, "mqueue", self._mq)
        
    def _hparams(self, params):
        """
            @param params: dictionary 
        """
        self.block   = params.get("block",   True)
        self.timeout = params.get("timeout", 0.1)
        
    def _hpump(self, *p):
        """ Message Pump
        
            Pulls (if possible) messages from the
            input queue and processes them
        """
        self.process(self.block, self.timeout)
        
    def _hproc_starting(self, name):
        """ Sent by the forked process upon starting
            its operations. Hence, this message marks
            the "birth" of a Child process.
            
            Thus, the Message Switch (this class ;-)
            must adapt its configuration.
        """
        self._name=name
        self._child=True
        self._reset()
        
        procDetails=self._subs[name]
        self._iq=procDetails["iq"]
        
    def _hxsub(self, mtype):
        """ Subscription to the Main/Parent 
            Message Switch publications
            
            Used to configure the Main/Parent
            Message Switch for local delivery of messages
            of a specified type
            
            If this instance exists in a Child process,
            then the subscription request must be sent
            upstream to the Main/Parent process where
            all communications converge.
            
            If, on the contrary, this instance is the
            Main/Parent process, we just have to "bridge"
            the messages transiting through here onto
            the local Message Bus.
        """
        if self._child:
            self._mq.put(["_sub", self._name, mtype])
        else:
            self._map[mtype] = True
        
    def _hxbridge(self, mtype):
        """ Configures the Switch for bridging 
            the specified message type
            
            This configuration will enable this instance
            to listen on the local Message Bus for the
            specified message-type and "bridge" any much
            message toward the "subscribers".
        """
        def makeThunk(mtype):
            def _thunk(*p):
                return self._hmbus(mtype, *p)
            return _thunk
            
        ## We need a `thunk` to hold the message-type
        ##  as when the message is delivered it won't
        ##  carry this essential information
        Bus.subscribe(mtype, makeThunk(mtype))
        
    def _hmbus(self, mtype, *p):
        """ Send a message upstream
        """
        msg=[mtype].extend(p)
        self._mq.put(msg)
    
        
    ## ===============================================    
    ## ===============================================
        
        
    def _processMsg(self, msg):
        try:    mtype=msg[0]
        except: mtype=None
        
        if not mtype:
            self._log("missing message type")
            return True
        
        if mtype=="_sub":
            self._handleSub(msg)
            return True
        
        if mtype=="_quit":
            return False
        
        return self._handleMsg(mtype, msg)

    def _handleMsg(self, mtype, msg):
        """Performs message dispatching
        """
        
        ## If we are a Child instance and we receive
        ##  a message, that means we have already subscribed
        ##  to be a recipient of this message type.  Just
        ##  pass it on the local Message Bus then.
        if self._child:
            Bus.publish(self, mtype, msg)
            return True
        
        #Bus.publish(self, "log", "_handleMsg(%s)" % mtype)
        subs=self._map.get(mtype, [])
        if not subs:
            self._log("no subscribers for type(%s)" % mtype)
            return True
        
        for proc_name in subs:
            q=self._qmap.get(proc_name, None)
            if q is None:
                self._log("error", "missing 'queue' object for proc(%s)" % proc_name)
                continue
            q.put(msg)
            #self._log("queued, type(%s) for proc(%s)" % (mtype, proc_name))
        return True
        
    def _handleSub(self, msg):
        """Handles subscription from child processes
        
            ["_sub", $mtype, $proc_name]
               0       1         2
        """
        
        ## A child doesn't have to respond
        ##  to this sort of request
        ## @todo: generate log?
        if self._child:
            return
        
        try:    pname=msg[1]
        except: pname=None
        
        try:    mtype=msg[2]
        except: mtype=None
        
        if pname is None:
            self._log("sub: `proc_name` missing for mtype(%s)" % mtype)
            return
        
        if mtype is None:
            self._log("sub: `mtype` missing for proc_name(%s)" % pname)
            return
        
        subs=self._map.get(mtype, [])
        subs.append(pname)
        self._map[mtype]=subs
            

## ================================================================

_centralInputQueue=Queue()
_centralInputQueue.cancel_join_thread()
_mswitch=MessageSwitch(_centralInputQueue)
        
Bus.subscribe("_sub",           _mswitch._hsub)
Bus.subscribe("proc",           _mswitch._hproc)
Bus.subscribe("start",          _mswitch._hstart)

Bus.subscribe("mqueue?",        _mswitch._qmqueue)
Bus.subscribe("mswitch_pump",   _mswitch._hpump)
Bus.subscribe("mswitch_params", _mswitch._hparams)

Bus.subscribe("proc_starting",  _mswitch._hproc_starting)
Bus.subscribe("xsub",           _mswitch._hxsub)
Bus.subscribe("xbridge",        _mswitch._hxbridge)

