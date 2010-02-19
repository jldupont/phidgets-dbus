"""
    Message Switch
    ==============
    
    The Message Switch is first initialized as if it
    was part of the Main Process.
    
    When a "proc_starting" message is received, the
    "personality" of the MSWITCH is updated. 
    
    
    
    @author: Jean-Lou Dupont
    Created on 2010-02-17
"""
__all__=[]

from phidgetsdbus.mbus import Bus

from Queue import Empty, Full
from multiprocessing import Queue


class MessageSwitch(object):
    """
    Message Format:
    
        [$mtype, $process_name, ...]
    """
    
    MAIN_PNAME="__main__"
    
    def __init__(self):
        self.mq=Queue()
        
        ## Subscription map
        ##  when acting as "main process switch"
        self._subs={}
        
        ## assume we start as being
        ## the Main process
        self._child=False
        self._pname=self.MAIN_PNAME
        self._mainq = self.mq
        
        ## Process map
        ##  pname -> mqueue
        self._pmap = {self._pname: self.mq}

        self._reset()
        
    def _reset(self):
        self.block=True
        self.timeout=0.1
        
    def _hproc_starting(self, pname):
        """ Child process starting
            Change pname name and "personality"
            
            We need to pick a message queue for
            our Child process.
            
            We also need to instruct the Main 
            process of this fact.
        """
        self._child=True
        self._pname=pname
        self.mq=Queue()
        
        self._sendToMain(["_procqueue", pname, self.mq])  #### MSG ####
        
        
    def _hproc(self, procDetails):
        """ Process Details
        
            We are just interested in the mapping
            { process_name : process_message_queue }
        """
        try:    name=procDetails["name"]
        except: raise RuntimeError("missing `name` entry in `procDetails`")
        
        try:    mq=procDetails["mq"]
        except: raise RuntimeError("missing `mq` entry in `procDetails`")

        self._pmap[name]=mq

    def _hsub(self, msgType):
        """ A local Client is interested in "msgType"
        
            If we are a Child process, we need to propagate
            this request to the Main process
        """
        msg=["_sub", self._pname, msgType]  #### MSG ####
        if self._child:
            self._sendToMain(msg)
        else:
            self._sendToChildren(msg)
        
    def _sendToMain(self, msg):
        """ Sends a message to the Main process
        """
        self._mainq.put(msg)
        
    def _sendToChildren(self, msg):
        """ Propagate a message down to all Child processes
        """
        for pname in self._pmap:
            try: q=self._pmap["mq"]
            except:
                raise RuntimeError("missing `mq` field associated with process(%s)" % pname)
            if pname != self.MAIN_PNAME:
                q.put(msg)
        
    def _getMsg(self):
        
        try:          msg=self.mq.get(self.block, self.timeout)
        except Full:  msg=None
        except Empty: msg=None
        
        return msg

    def _hpump(self):
        """ Pulls message(s) (if any) from the message queue
        
            A Child process:
            - "_sub"  : locally subscribe the Main process to msgType
                        This will send all local messages of msgType
                        up to the Main process where it can
                        be further distributed (multicasted)
            - "_procqueue" : *shouldn't* receive this sort of message
            
            The Main process:
            - "_sub" : 
                - subscribe locally from Message Bus
                - send down to all Children in "split-horizon"
            - "_procqueue" : 
                - update local mapping
        """
        msg = self._getMsg()
        if msg is None:
            return
        
        try:   mtype=msg.pop(0)
        except:
            raise RuntimeError("invalid message format, missing `mtype` field in list")
        
        try:   spname=msg.pop(0)
        except:
            raise RuntimeError("invalid message format, missing `pname` field in list")
        
        if self._child:
            self._hpumpChild(mtype, spname, msg)
        else:
            self._hpumpMain(mtype, spname, msg)
            
    def _hpumpChild(self, mtype, spname, msg):
        if mtype=="_sub":
            try:    msgtype=msg.pop(0)
            except:
                raise RuntimeError("missing `msgType` from `_sub` message")
            self._addSub(self.MAIN_PNAME, msgtype)
            return
        
        ## All other "system" messages are ignored
        if mtype.startswith("_"):
            return
        
        ## Finally, publish whatever message we receive
        ##  from the Main process: we should have subscribed
        ##  to these anyhow (unless of course there is a bug ;-)
        Bus.publish(self, mtype, msg)
    
    def _hpumpMain(self, mtype, spname, msg):
        if mtype=="_sub":
            try:    msgtype=msg.pop(0)
            except:
                raise RuntimeError("missing `msgType` from `_sub` message")           
            self._addSub(spname, msgtype)
            
            ## repeat source message
            self._sendSplitHorizon(mtype, spname, [msgtype])
            return

        if mtype=="_procqueue":
            try:    q = msg.pop(0)
            except:
                raise RuntimeError("missing `queue` parameter for message(%s)" % mtype)
            self._pmap[spname] = q
            return
        
    

    def _addSub(self, pname, msgType):
        """ Adds a subscriber (a process) to
            a publishing list for "msgType"
        """
        subs=self._subs.get(msgType, [])
        subs.extend(pname)
        self._subs[msgType]=subs

    def _sendSplitHorizon(self, mtype, spname, msgTail):
        msg=[mtype, spname].extend(msgTail)
        for pname in self._pmap:
            
            ## split horizon i.e. not back to source
            if pname==spname:
                continue
            
            ## not to self also !!
            if pname==self.MAIN_PNAME:
                continue
            
            q=self._pmap[pname]
            q.put(msg)














class MessageSwitch2(object):
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

