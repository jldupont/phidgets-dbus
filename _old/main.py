"""
    @author: jldupont
"""
__all__=[ "ProcessClass" ]

import multiprocessing


class _ProcessManager(object):
    """
    """
    def __init__(self):
        self._procs=[]
        
    def add(self, className):
        pass
    
    def start(self):
        """
        Start all the processes
        """
    
    def joins(self):
        """
        Join all the processes
        """
    
    
processManager=_ProcessManager()




class ProcessBase(multiprocessing.Process):
    """
    """
    def __init__(self):
        multiprocessing.Process.__init__(self)
        
    def txMsg(self, msg):
        pass

    def subscribeMsgType(self, msgType):
        pass

