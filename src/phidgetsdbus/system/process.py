"""
    Process class definition 

    Bus Messages:
    =============
    
    Publishes:
    
    - "proc" : sent when a process is defined
    - "proc_starting" : sent just before executing the "doRun" method on the process

    Subscribes:
    
    - "_ready" : to signal when all other processes are "ready"

    System
    -----------
    The lifecycle of a "process" consists of 2 stages:
    - BEFORE the "fork" : process is being prepared for spawning
    - AFTER the "fork"  : process is spawned
    

    @author: Jean-Lou Dupont
    Created on 2010-02-16
"""
__all__=["ProcessClass"]

from multiprocessing import Process, Queue

from phidgetsdbus.mbus import Bus

class ProcessClass(Process):
    
    def __init__(self, name):
        Process.__init__(self)
        self.pqueue=Queue()
        self.name=name
        self.term=False
        
        Bus.subscribe("_sigterm", self._hsigterm)
        
        ## Publish the proc's details over the local message bus
        ##  The ProcessManager will need those details in order to
        ##  launch the process later on.
        Bus.publish(self, "proc", {"proc":self, "name":name, "queue":self.pqueue})
           
    def is_SigTerm(self):
        return self.term 
           
    def _hsigterm(self):
        self.term=True
               
    def _hready(self):
        """ Handles the "_ready" message
        """
        _hldr=getattr(self, "hready", None)
        if _hldr is not None:
            _hldr()
               
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
        
        Bus.subscribe("_ready", self._hready)
        
        ## Announce to the Agents we are starting and, incidentally,
        ## that "we" are a "Child" process
        Bus.publish(self, "proc_starting", (self.name, self.pqueue))
        return self.doRun()
        
    def doRun(self):
        """ This method needs to be subclassed
        
            ATTENTION: do not subclass the `run` method
            as it is normally the case when using the
            `multiprocessing.Process` base class
        """
        raise RuntimeError("this needs to be subclassed")

