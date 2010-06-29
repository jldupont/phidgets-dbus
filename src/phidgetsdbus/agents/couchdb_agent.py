"""
    Couchdb Agent

    - create db *if* not exists
    - log db creation error - rate limited
    - accumulate states
    - write states
    
    @author: jldupont
    Created on Jun 26, 2010
"""

from system.base import AgentThreadedBase
import system.db as d
from system.dtype import BoundedList
 

class CouchdbAgent(AgentThreadedBase):
    
    MAX_BACKLOG=128
    BACKOFF_LIMIT=64 ## seconds
    MAX_BURST_SIZE=4
    C_LOGPARAMS=[("db_creation_error", "error", 2)
                ,("db_creation_ok",   "info",  8)
                ]
    
    def __init__(self):
        AgentThreadedBase.__init__(self)

        self.retry_count=0
        self.smap={}
        self.last_retry_count=1
        self.retry_count=0
        self.db_ok=None
        self.todo=BoundedList(self.MAX_BACKLOG)

    ## =========================================================================== HANDLERS
    
    def h_ready(self):
        self._try_create()

    def h_timer_second(self, count):
        """
        Time base
        """
        if not self.ready:
            return
        
        if not self.db_ok:
            self._doHandleDb()


    def h_timer_minute(self, count):
        """
        Time base
        """
        
    def h_sensor(self, deviceId, sensorId, value):
        """
        Keep a map of sensor state 
        """
        previousValue=self.smap.get((deviceId, sensorId), None)
        if previousValue is None or value!=previousValue:
            self.todo.push((deviceId, sensorId, value))
            self.smap[(deviceId, sensorId)]=value
            self.dprint(">>> Changed, device(%s) sensor(%s) value(%s)" % (deviceId, sensorId, value))

    ## =========================================================================== HELPERS
    def _try_create(self):
        self.db_ok = d.db.create()

        if not self.db_ok:
            self.pub("log", "db_creation_error", "Error creating database on couchdb")
        else:
            self.pub("log", "db_creation_ok", "Created database on couchdb")
        

    def _doHandleDb(self):
        """
        Retries connecting to couchdb, uses back-off
        """
        if self.retry_count == 0:
            self._try_create()
            
            if self.last_retry_count >= self.BACKOFF_LIMIT:
                self.last_retry_count = 1
                
            ## back-off
            self.retry_count = self.last_retry_count * 2
            self.last_retry_count = self.retry_count
            
            self.dprint("retrying in %s seconds" % str(self.retry_count))
        else:
            self.retry_count -= 1
            
        

_=CouchdbAgent()
_.start()
