"""
    Daemon Application wrapper
    
    @author: Jean-Lou Dupont 
"""
import os

__all__=["app",]

class AppAgent(object):
    
    APPNAME="phidgetsdbus"
    BASEPATH="~/.phidgetsdbus"
    
    def __init__(self):
        basepath=os.path.expanduser(os.path.expandvars(self.BASEPATH))
        
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
        log.path=self.BASEPATH
        log.name=self.APPNAME
        
        try:
            import dbus.glib
            import gobject              #@UnresolvedImport
            
            gobject.threads_init()
            dbus.glib.init_threads()
            
            from dbus.mainloop.glib import DBusGMainLoop
            DBusGMainLoop(set_as_default=True)
            #glib.threads_init()

            import phidgetsdbus.api     #@UnresolvedImport
        
            log("Starting - pid: %s" % os.getpid())
            loop = gobject.MainLoop()
            gobject.timeout_add(1000, self.setup)
            loop.run()
        except Exception,e:
            log("error", "exception: %s" % e)

    def setup(self):
        import phidgetsdbus.phidget #@UnresolvedImport
        return False
    
    
app=AppAgent()
