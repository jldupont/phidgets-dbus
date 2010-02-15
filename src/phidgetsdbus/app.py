"""
    Daemon Application wrapper
    
    @author: Jean-Lou Dupont 
"""
__all__=["app",]

class AppAgent(object):
    def __init__(self):
        self.stdin_path="/dev/null"
        self.stdout_path="/var/log/phidgetsdbus.out"
        self.stderr_path="/var/log/phidgetsdbus.err"
        self.pidfile_path="/var/run/phidgetsdbus"
        self.pidfile_timeout=2
    
    def run(self):
        """
        Deferred application loading & running
        """
        from phidgetsdbus.logger import log 
        log.name="phidgetsdbus"
        
        try:
            import phidgetsdbus.api   #@UnusedImport
            import gtk                #@UnresolvedImport
            import os
        
            log("Starting - pid: %s" % os.getpid())
            gtk.main()
        except Exception,e:
            log("error", "exception: %s" % e)

    
app=AppAgent()

