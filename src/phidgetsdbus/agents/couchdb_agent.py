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


class CouchdbAgent(AgentThreadedBase):
    
    BACKOFF_LIMIT=128 ## seconds
    
    def __init__(self):
        AgentThreadedBase.__init__(self)

        self.retry_count=0
        self.smap={}
        self.db_detected=False

    def h_timer_second(self, count):
        """
        Time base
        """

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
_.start
