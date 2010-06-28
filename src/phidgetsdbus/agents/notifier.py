"""
    @author: jldupont

    Created on Jun 28, 2010
"""
import pynotify

from system.base import AgentThreadedBase

class NotifierAgent(AgentThreadedBase):
    def __init__(self, app_name):
        AgentThreadedBase.__init__(self)
        self.app_name=app_name
        pynotify.init(app_name)        
        self.types=["w", "e", "warning", "error"]
        
    def h_logged(self, _logtype, loglevel, msg):
        #print "Notifier.h_logged, logtype(%s)" % logtype
        if loglevel in self.types:
            
            n=pynotify.Notification(self.app_name, msg)
            n.set_urgency(pynotify.URGENCY_CRITICAL)
            n.show()
            
"""
_=NotifierAgent(APP_NAME)
_.start()
"""        
        