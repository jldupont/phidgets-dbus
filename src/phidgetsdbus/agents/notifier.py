"""
    Notifier Agent
    
    Uses 'pynotify' (desktop notification) to message
    the user in case of 'warning' and 'error' level log entries
    
    @author: jldupont

    Created on Jun 28, 2010
"""
import pynotify

from system.base import AgentThreadedBase

class NotifierAgent(AgentThreadedBase):
    def __init__(self, app_name, icon_name):
        AgentThreadedBase.__init__(self)
        self.app_name=app_name
        self.icon_name=icon_name
        pynotify.init(app_name)        
        self.types=["w", "e", "warning", "error"]
        
    def h_logged(self, _logtype, loglevel, msg):
        #print "Notifier.h_logged, logtype(%s)" % logtype
        if loglevel in self.types:
            
            n=pynotify.Notification(self.app_name, msg, self.icon_name)
            n.set_urgency(pynotify.URGENCY_CRITICAL)
            n.show()
            
"""
_=NotifierAgent(APP_NAME)
_.start()
"""        
        