"""
    Simple "Bus" based message publish/subscribe

    - Announces "client" subscriptions through
      a special message "_sub"
      
    - "Promiscuous" subscription supported
      through using the "*" as message type upon
      performing subscription
      
    @todo: add support for cyclic publication condition

    Created on 2010-01-28
    @author: jldupont
"""

__all__=["Bus"]

class Bus(object):
    """
    Simple publish/subscribe "message bus"
    with configurable error reporting
    
    Message delivery is "synchronous i.e. the caller of
    the "publish" method blocks until all the subscribers
    of the message have been "called-back".
    
    Any "callback" can return "True" for stopping the
    calling chain.
    """
    debug=False
    logger=None
    ftable={}
    sendMsgType=False

    @classmethod
    def _maybeLog(cls, msgType, msg):
        """
        Private - Logging helper
        """
        if not cls.debug:
            return
        
        if msgType=="log":
            return
        
        if cls.logger:
            cls.logger(msg)
    
    @classmethod
    def reset(cls):
        """ Resets the Bus to a known state
        
            This is especially useful when, as example,
            a process is spawn whilst the parent had a
            configured Bus instance.  The child process
            calls this method upon starting in order to
            fall back to a known state before proceeding
            to accept new subscriptions.
        """
        #cls.ftable={}
        cls.logger=None
        cls.sendMsgType=False
    
    @classmethod
    def subscribe(cls, msgType, callback):
        """
        Subscribe to a Message Type
        
        The "msgType" can be "*" to accept promiscuous subscriptions.
        
        @param msgType: string, unique message-type identifier
        @param callback: callable instance which will be called upon message delivery  
        """
        try:
            cls._maybeLog(msgType, "subscribe: subscriber(%s) msgType(%s)" % (callback.__self__, msgType))
            subs=cls.ftable.get(msgType, [])
            subs.append((callback.__self__, callback))
            cls.ftable[msgType]=subs
        except Exception, e:
            cls._maybeLog(msgType, "Exception: subscribe: %s" % str(e))
            
        ## Announce the subscriptions
        ##  This step is useful for "message bridges"
        cls.publish("__bus__", "_sub", msgType)
        
    @classmethod
    def publish(cls, caller, msgType, *pa, **kwa):
        """
        Publish a message from a specific type on the bus
        
        @param msgType: string, message-type
        @param *pa:   positional arguments
        @param **kwa: keyword based arguments
        """
        cls._maybeLog(msgType, "BUS.publish: type(%s) caller(%s) pa(%s) kwa(%s)" % (msgType, caller, pa, kwa))
        subs=cls.ftable.get(msgType, [])
        if not subs:
            cls._maybeLog(msgType, "Bus.publish: no subs")
            
        ## First, do the normal subscribers
        cls._doPub(subs, caller, msgType, *pa, **kwa)
        
        ## Second, do the "promiscuous" subscribers
        psubs=cls.ftable.get("*", [])
        cls._doPub(psubs, caller, msgType, *pa, **kwa)

    @classmethod
    def _doPub(cls, subs, caller, msgType, *pa, **kwa):
        for (sub, cb) in subs:
            if sub==caller:  ## don't send to self
                continue
            try:
                if cls.sendMsgType:
                    stop_chain=cb(msgType, *pa, **kwa)
                else:
                    stop_chain=cb(*pa, **kwa)
            except IOError:
                raise
            """
            except Exception, e:
                print "*** Bus.publish: exception: ",e
                stop_chain=True    
                if cls.logger:
                    cls.logger("Exception: msgType(%s): %s" %( msgType, str(e)))
            """
            if stop_chain:
                print "Bus.publish: chain stopped, type(%s)" % msgType
                break
