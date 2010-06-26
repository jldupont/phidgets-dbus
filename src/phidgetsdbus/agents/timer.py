"""
    Timer Agent
    
    MESSAGES IN:
    - "tick"
    
    MESSAGES OUT:
    - "timer_second"
    - "timer_minute"
    - "timer_hour"
    - "timer_day"

    @author: jldupont

    Created on Jun 25, 2010
"""
from system.base import AgentThreadedBase

class TimerAgent(AgentThreadedBase):

    def __init__(self):
        AgentThreadedBase.__init__(self)

        self.freq=0
        
        self.tcount=0
        self.scount=0
        self.mcount=0
        self.hcount=0
        self.dcount=0
        
    def h_tick_params(self, freq):
        self.freq=freq

    def h_tick(self, *_):
        #print "TimerAgent.h_tick"
        self.tcount += 1
        if self.tcount == self.freq:
            self.tcount = 0
            self.scount += 1
            self.pub("timer_second", self.scount)
        
        if self.scount == 60:
            self.scount = 0
            self.mcount += 1
            self.pub("timer_minute", self.mcount)
            
        if self.mcount == 60:
            self.mcount = 0
            self.hcount += 1
            self.pub("timer_hour", self.hcount)
            
        if self.hcount == 24:
            self.hcount = 0
            self.dcount += 1
            self.pub("timer_day", self.dcount)


_=TimerAgent()
_.start()
