"""
    Sync Agent
    
    - Announces which Agents are ready to all through the "agent?" message
    - Announces 'synced' when all Agents are ready
    
    MESSAGES IN:
    - timer_second
    - agent
    
    MESSAGES OUT:
    - agent?
    - synced
    
    @author: jldupont

    Created on Jun 28, 2010
"""
__all__=["SyncAgent"]
from system.base import AgentThreadedBase

class SyncAgent(AgentThreadedBase):
    """
    @param agents: list of Agents to wait for
    """
    PERIOD=10
    
    def __init__(self, agents):
        """
        @param agents: list of agents to monitor
        """
        AgentThreadedBase.__init__(self)
        self.targets=agents
        self.agent_count=len(agents)
        self.agents=[]
        self.count=0
        
    def h_timer_second(self, count):
        if self.count > self.PERIOD:
            return

        self.count+=1
                
        if len(self.agents) >= self.agent_count: 
            self.pub("synced")
            return
        
        self.pub("agent?", self.agents)
        
    def h_agent(self, agent_name):
        if agent_name not in self.agents:
            self.agents.append(agent_name)
            print "Agent(%s) sync'ed" % agent_name

"""
_=SyncAgent(AGENT_COUNT)
_.start()
"""