#!/usr/bin/env python
"""
    @author: Jean-Lou Dupont
"""
import os
import sys

## For development environment
ppkg=os.path.abspath( os.getcwd() +"/phidgetsdbus")
if os.path.exists(ppkg):
    sys.path.insert(0, ppkg)

from phidgetsdbus.daemon.runner import DaemonRunner, DaemonRunnerStopFailureError, DaemonRunnerStartFailureError


def errorMsg(msg, exitCode=1):
    from phidgetsdbus.terminal import render 
    print render("%(BOLD)s %(RED)s Error:%(NORMAL)s "+msg)
    sys.exit(exitCode)
    
try:
    from phidgetsdbus.app import app     
    dr=DaemonRunner(app)
    dr.parse_args(sys.argv)
except IOError,e:
    errorMsg("Permission error (%s)" % e)
except Exception,e:
    errorMsg("Unexpected error (%s)" % e)

try:
    dr.do_action()
except DaemonRunnerStopFailureError,e:
    errorMsg( "! Can't stop daemon - is one actually running? (%s)" % e )
except DaemonRunnerStartFailureError,e:
    errorMsg( "! Can't start daemon - is one actually running? (%s)" % e )
except Exception,e:
    errorMsg( "unexpected error: %s" % e )
    
## Will be executed in the daemon context
## Must initialize the logger
from phidgetsdbus.logger import log
log.path="~/.phidgetsdbus"
log.name="phidgetsdbus"
log("Ending")
