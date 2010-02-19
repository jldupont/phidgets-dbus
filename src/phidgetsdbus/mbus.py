"""
    Simple "Bus" based message publish/subscribe

    Created on 2010-01-28

    @author: jldupont
"""

__all__=["Bus"]

class sQueue(object):
    """
    Simple Queue class - not thread safe
    """
    def __init__(self):
        self.queue=[]
        
    def push(self, el):
        self.queue.append(el)
        return self
    
    def pop(self):
        try:     el=self.queue.pop(0)
        except:  el=None
        return el

    def clear(self):
        self.queue = []

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
    q=sQueue()
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
        cls.q.clear()
    
    @classmethod
    def subscribe(cls, msgType, callback):
        """
        Subscribe to a Message Type
        
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
        
    @classmethod
    def publish(cls, caller, msgType, *pa, **kwa):
        """
        Publish a message from a specific type on the bus
        
        @param msgType: string, message-type
        @param *pa:   positional arguments
        @param **kwa: keyword based arguments
        """
        #cls._maybeLog(msgType, "BUS: publish:BEGIN - Queue processing")
        while True:
            cls._maybeLog(msgType, "BUS.publish: type(%s) caller(%s) pa(%s) kwa(%s)" % (msgType, caller, pa, kwa))
            subs=cls.ftable.get(msgType, [])
            if not subs:
                cls._maybeLog(msgType, "Bus.publish: no subs")
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
                except Exception, e:
                    print "*** Bus.publish: exception: ",e
                    stop_chain=True    
                    if cls.logger:
                        cls.logger("Exception: msgType(%s): %s" %( msgType, str(e)))
                if stop_chain:
                    print "Bus.publish: chain stopped, type(%s)" % msgType
                    break

            msg=cls.q.pop()
            if not msg:
                break
            caller, msgType, pa, kwa = msg
        

