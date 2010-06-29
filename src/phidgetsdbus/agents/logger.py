"""
    LoggerAgent
    
    A configurable logging agent with rate limiting
    
    MESSAGES IN:
    - timer_day
    - logparams
    - log
    
    MESSAGES OUT:
    - logged : useful to other agents - rate limiting enforced here
    
    @author: jldupont
    Created on Jun 25, 2010
"""
import os
import logging

from system.base import AgentThreadedBase


class LoggerAgent(AgentThreadedBase):
    """
    Configurable Logging Agent
    
    1- Use the "config_params" to configure individual "log message type"
    3- Use the "log" message to actually log a message
    """
    
    mlevel={"info":     logging.INFO
            ,"warning": logging.WARNING
            ,"error":   logging.ERROR
            ,"i":       logging.INFO
            ,"w":       logging.WARNING
            ,"e":       logging.ERROR
            }
    
    def __init__(self, name, path):
        AgentThreadedBase.__init__(self)
        self.name=name
        self.path=path
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
    
    def config_params(self, agent, entries):
        self.h_logparams(agent, entries)
    
    def h_logparams(self, agent, entries):
        """
        Set the parameters associated with a log type
        
        @param logtype:  string, message log type
        @param loglevel: string, [info, warning, error]
        @param lograte:  integer, maximum number of messages of logtype per day
        @param console_on_limit: [optional] boolean, True: output message to console if rate limited
        """
        if len(entries) == 0:
            return

        try:
            for entry in entries:
                try:
                    (logtype, loglevel, lograte, console_on_limit)=entry
                except:
                    (logtype, loglevel, lograte)=entry
                    console_on_limit=False
                self.map[logtype] = (loglevel, lograte, console_on_limit)
        except:
            print "*** LoggerAgent: error whilst processing 'logparams' entries from Agent(%s)" % agent

    def h_log(self, logtype, msg):
        """
        Handles the "log" message
        """
        if self._logger is None:
            self._setup()
            
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
        self.pub("logged", logtype, level, msg)
        
        ## update stats - rate limiting
        self.stats[logtype] = current_count+1
            
    def h_shutdown(self, *_):
        self._shutdown=True        
        if self._logger is not None:
            logging.shutdown([self.fhdlr])
            self.fhdlr=None
            self._logger=None            
            
    ## ================================================================================ HELPERS        
    def _setup(self):
        self._logger=logging.getLogger(self.name)
        
        path=os.path.expandvars(os.path.expanduser(self.path))
        self.fhdlr=logging.FileHandler(path)
        
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        self.fhdlr.setFormatter(formatter)
        self._logger.addHandler(self.fhdlr)
        self._logger.setLevel(logging.INFO)

        
        
