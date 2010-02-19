"""
    Process class definition 

    Bus Messages:
    =============
    - "proc" : sent when a process is defined
    - "_sub" : sent during the process execution 
                to signal a request for subscription to a `message type`  

    - "proc_running" : sent when a process is about to be be "run" 

    - "mqueue" : grab the `mqueue` parameter for the back communication channel

    System
    -----------
    The lifecycle of a "process" consists of 2 stages:
    - BEFORE the "fork" : process is being prepared for spawning
    - AFTER the "fork"  : process is spawned
    

    @author: Jean-Lou Dupont
    Created on 2010-02-16
"""
__all__=["ProcessClass"]

from multiprocessing import Process

from phidgetsdbus.mbus import Bus

class ProcessClass(Process):
    
    def __init__(self, name):
        Process.__init__(self)
       
        self.name=name
        
        ## Publish the proc's details over the local message bus
        ##  The ProcessManager will need those details in order to
        ##  launch the process later on.
        Bus.publish(self, "proc", {"proc":self, "name":name})
        
        ## Prior to the fork, we need the `mqueue` parameter
        Bus.subscribe("mqueue", self._hmqueue)
        
    def _hmqueue(self, mq):
        """ Handler for the "mqueue" message type
        
            Useful during the forking phase - this parameter
            is important to a child process in order to communicate
            back with the Main (parent) process 
        """
        self._mq=mq
        
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
        return self.doRun()
        
    def doRun(self):
        """ This method needs to be subclassed
        
            ATTENTION: do not subclass the `run` method
            as it is normally the case when using the
            `multiprocessing.Process` base class
        """
        raise RuntimeError("this needs to be subclassed")

