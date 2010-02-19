"""
    Process Manager

    - Gathers process registration
    - Performs process start

    @author: jldupont
    Created on 2010-02-17
"""
__all__=[]

from phidgetsdbus.mbus import Bus

class ProcessManager(object):
    
    def __init__(self):
        self._name = "__main__"  ##default
        self._mq=None
        self._procs={}

    def _hproc_starting(self, (pname, _)):
        """ Handler for "proc_starting"
        
            Marks the start of a Child process
        """
        self._name=pname
        
    def _qpname(self):
        """ Answer for the question "pname?"
        """
        Bus.publish(self, "pname", self._name)
        
    def _hproc(self, procDetails):
        """ Handler dealing with "register process"
            
            @param procDetails: dictionary 
        """
        try:    name=procDetails.get("name", None)
        except: raise RuntimeError("procDetails require a `name` entry")

        ## Accumulate `process details` just in
        ##  case we enhance the system :-)
        proc=self._procs.get(name, {})
        proc.update(procDetails)
        self._procs[name]=proc
        
    def _hstart(self):
        """ Handler for "start" message
            marking the debut of all registered processes
            
            The parameter `mq` (message queue) is injected
            in the process callable before actually starting
            it: this way, upon successfully "fork", the 
            multiprocessing module will call the "run" method 
            of the process callable and the wiring to the
            message switch will be performed.
        """
        
        for proc_name in self._procs:
            procDetails=self._procs[proc_name]
            try:     proc=procDetails["proc"]
            except:  raise RuntimeError("procDetails require a `proc` entry")
                
            try:
                print "pman (%s)" % procDetails["name"]
                Bus.publish(self, "log", "< starting process(%s)" % procDetails["name"])
                proc.start()
                Bus.publish(self, "log", "> started process(%s)" % procDetails["name"])
            except Exception,e:
                raise RuntimeError("Exception whilst starting process (%s)" % e)
                

_pm=ProcessManager()
Bus.subscribe("start",          _pm._hstart)
Bus.subscribe("proc",           _pm._hproc)
Bus.subscribe("pname?",         _pm._qpname)
Bus.subscribe("proc_starting",  _pm._hproc_starting)
