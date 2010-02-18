"""
    Process class definition 

    Bus Messages:
    =============
    - "proc" : sent when a process is defined
    - "_sub" : sent during the process execution 
                to signal a request for subscription to a `message type`  

    - "proc_running" : sent when a process is about to be be "run" 

    System
    -----------
    The lifecycle of a "process" consists of 2 stages:
    - BEFORE the "fork" : process is being prepared for spawning
    - AFTER the "fork"  : process is spawned
    

    @author: Jean-Lou Dupont
    Created on 2010-02-16
"""
__all__=["ProcessClass"]

from Queue import Full, Empty
from multiprocessing import Process, Queue

from phidgetsdbus.mbus import Bus

class ProcessClass(Process):
    """
    Parameter `_mq` will get configured by the Process Manager
    """
    def __init__(self, name):
        Process.__init__(self)
        
        self.name=name
        self._mq = None
        self._iq = Queue()
        self._iq.cancel_join_thread()
        
        ## Publish the proc's details over the local message bus
        ##  The ProcessManager will need those details in order to
        ##  launch the process later on.
        ##  The MessageSwitch will also need the "iq" queue in order
        ##  to correlate a process {Name:Queue} for communications.
        Bus.publish(self, "proc", {"proc":self, "name":name, "iq": self._iq})
        
    def run(self):
        """ Called by the multiprocessing module
            once the process is ready to run i.e. after the "fork"
            
            We intercept this call in order to make the
            final preparation before handing the control
            to the user process
        """
        ## For now, there isn't that much to do
        ##  except to reset the process level Message Bus
        ##  to a known start state
        Bus.reset()
        
        ## Announce to the Agents we are starting and, incidentally,
        ## that "we" are a "Child" process
        Bus.publish(self, "proc_starting", self.name)
        ##self.publish(["proc_starting", self.name])
        return self.doRun()
        
    def doRun(self):
        """ This method needs to be subclassed
        
            ATTENTION: do not subclass the `run` method
            as it is normally the case when using the
            `multiprocessing.Process` base class
        """
        raise RuntimeError("this needs to be subclassed")

    def publish(self, msg):
        """ Sends a "publish" command to the central Message Switch
        """
        self._mq.put(msg)
        
    def subscribe(self, mtype):
        """ Sends a "subscription" command to the central Message Switch
        """
        self.publish(["_sub", self.name, mtype])
    
    def getMsg(self, block=True, timeout=0.1):
        """ Retrieves (if possible) a message from the queue
        
            @return None: no message present *but* communication is OK
            @raise EOFError: upon communication error 
        """
        try:   msg=self._iq.get(block, timeout)
        except Empty: msg=None
        except Full:  msg=None
        return msg

