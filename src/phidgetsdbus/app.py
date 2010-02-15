"""
    Daemon Application wrapper
    
    @author: Jean-Lou Dupont 
"""
import os

__all__=["app",]

class AppAgent(object):
    def __init__(self):
        basepath=os.path.expanduser(os.path.expandvars("~/.phidgetsdbus"))
        
        self.stdin_path="/dev/null"
        self.stdout_path="/dev/null"
        self.stderr_path=basepath+"/stderr"
        self.pidfile_path=basepath+"/pid"
        self.pidfile_timeout=2
    
    def run(self):
        """
        Deferred application loading & running
        """
        from phidgetsdbus.logger import log 
        log.path="~/.phidgetsdbus"
        log.name="phidgetsdbus"
        
        try:
            from dbus.mainloop.glib import DBusGMainLoop
            DBusGMainLoop(set_as_default=True)

            import phidgetsdbus.api   #@UnusedImport
            import gobject            #@UnresolvedImport
        
            log("Starting - pid: %s" % os.getpid())
            loop = gobject.MainLoop()
            loop.run()
        except Exception,e:
            log("error", "exception: %s" % e)

    
app=AppAgent()
