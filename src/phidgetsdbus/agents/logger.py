"""
    LoggerAgent
    
    A configurable logging agent with rate limiting
    
    @author: jldupont
    Created on Jun 25, 2010
"""
import logging

from system.base import AgentThreadedBase


class LoggerAgent(AgentThreadedBase):
    """
    Configurable Logging Agent
    
    1- Use the "loginit" message to configure name & filesystem path for log file
    2- Use the "logparams" to configure individual "log message type"
    3- Use the "log" message to actually log a message
    """
    
    mlevel={"info":     logging.INFO
            ,"warning": logging.WARNING
            ,"error":   logging.ERROR
            }
    
    def __init__(self):
        AgentThreadedBase.__init__(self)
        self.name=None
        self.path=None
        self.map={}
        self.stats={}
        self._logger=None
        self._shutdown=False
        self.fhdlr=None
    
    ## ================================================================================ HANDLERS
    def h_timer_day(self, *_):
        """
        Marks the end/start of a new day
        """
        self.stats={}
    
    def h_loginit(self, name, path):
        """
        Handles the "loginit" message
        """
        self._name=name
        self._path=path
        self._setup()

    def h_logparams(self, logtype, loglevel, lograte, console_on_limit):
        """
        Set the parameters associated with a log type
        
        @param logtype:  string, message log type
        @param loglevel: string, [info, warning, error]
        @param lograte:  integer, maximum number of messages of logtype per day
        @param console_on_limit: boolean, True: output message to console if rate limited
        """
        self.map[logtype] = (loglevel, lograte)

    def h_log(self, logtype, msg):
        """
        Handles the "log" message
        """
        entry=self.map.get(logtype, None)
        if entry is None:
            entry=("info", 1, True)
            print "*** LoggerAgent: logtype(%s) undefined" % logtype
            
        current_count=self.stats.get(logtype, 0)
        level, limit, console=entry
        
        ## check for rate limit
        if limit is not None:
            if current_count > limit:
                if console:
                    print "*** %s: %s" % (level, msg)
                return
        
        self._logger.log(self.mlevel[level], msg)
        
        ## update stats - rate limiting
        self.stats[logtype] = current_count+1
            
    def h_shutdown(self, *_):
        self._shutdown=True
        self._logger=None
        logging.shutdown([self.fhdlr])
            
    ## ================================================================================ HELPERS        
    def _setup(self):
        self._logger=logging.getLogger(self._name)
        
        path=os.path.expandvars(os.path.expanduser(self._path))
        self.fhdlr=logging.FileHandler(path)
        
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        self.fhdlr.setFormatter(formatter)
        self._logger.addHandler(self.fhdlr)
        self._logger.setLevel(logging.INFO)

        
        
_=LoggerAgent()
_.start()
