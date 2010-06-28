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
 

class CouchdbAgent(AgentThreadedBase):
    
    BACKOFF_LIMIT=128 ## seconds
    LOGPARAMS=[("db_creation_error", "error", 2)
               ,("db_creation_ok",   "info",  8)
               ]
    
    def __init__(self):
        AgentThreadedBase.__init__(self)

        self.retry_count=0
        self.smap={}
        self.db_detected=False
        self.last_try_error=False

    def h_ready(self):
        self.pub("logparams", self.__class__, self.LOGPARAMS)

    def h_timer_second(self, count):
        """
        Time base
        """
        if not self.ready:
            return

        if not d.db.create():
            self.pub("log", "db_creation_error", "Error creating database on couchdb")
        else:
            self.pub("log", "db_creation_ok", "Created database on couchdb")       


    def h_timer_minute(self, count):
        """
        Time base
        """
        
    def h_sensor(self, deviceId, sensorId, value):
        """
        Keep a map of sensor state 
        """
        previousValue=self.smap.get((deviceId, sensorId), None)
        
        
_=CouchdbAgent()
_.start()
