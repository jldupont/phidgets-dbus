#!/usr/bin/env python
"""
    @author: Jean-Lou Dupont
"""
import sys
import os
import random
from time import sleep

ppkg=os.path.abspath( os.getcwd() +"/../src")
sys.path.insert(0, ppkg)

class _Printer(object):
    def __call__(self, msg):
        print "!Bus: ", msg


from phidgetsdbus.mbus import Bus
from phidgetsdbus.system.process import ProcessClass

from phidgetsdbus.agents import *

Bus.logger=_Printer()
#Bus.debug=True

Bus.publish(None, "logpath", "tmswitch", "~/tmswitch.log")


class TestProc(ProcessClass):
    def __init__(self, name):
        ProcessClass.__init__(self, name)

    def hready(self):
        print "TestProc (%s) ready!" % self.name        

    def doRun(self):
        print "TestProc.doRun (%s)" % self.name
        Bus.publish(self, "log", "starting (%s) pid(%s)" % (self.name, os.getpid()))
        try:
            while not self.is_SigTerm():
                Bus.publish(self, "mswitch_pump")

                #print "tick (%s)" % self.name
                Bus.publish(self, "tick", self.name, os.getpid())
                sleep(2.550+0.250*random.random())
                
            print ">>> Exiting (%s) <<<" % self.name
            
        except Exception,e:
            Bus.publish(self, "log", "*** (%s) Comm Exception: %s" % (self.name, e))
            print "TestProc: Exiting (%s)" % self.name
            Bus.publish(self, "log", "Exiting (%s)" % e)
            Bus.publish(self, "shutdown")


class TestProcRx(ProcessClass):
    def __init__(self, name):
        ProcessClass.__init__(self, name)
        self.ready=False

    def hready(self):
        print "TestProcRx (%s) ready!" % self.name
        self.ready=True
        Bus.subscribe("tick", self._htick)

    def doRun(self):
               
        print "TestProcRx.doRun (%s) pid(%s)" % (self.name, os.getpid())
        Bus.publish(self, "log", "doRun: starting (%s) pid(%s)" % (self.name, os.getpid()))
        
        while not self.is_SigTerm():
            try:
                Bus.publish(self, "mswitch_pump")
            except Exception,e:
                Bus.publish(self, "log", "*** (%s) Comm Exception: %s" % (self.name, e))
                Bus.publish(self, "shutdown")
                print "getMsg, exception: ", e
                break
            sleep(0.01)
        print ">>> Exiting (%s) <<<" % self.name

    def _htick(self, *pa):
        """
        """
        print "Tick, msg:",pa
 
## ==============================================================
## ==============================================================
import signal

_exitFlag=False

def _shandler(signum, _):
    print "signal handler: ", signum
    global _exitFlag
    _exitFlag=True

def _sChild(signum, _):
    print "_sChild: ", signum
    

#signal.signal(signal.SIGTERM, _shandler)
#signal.signal(signal.SIGKILL, _shandler)
signal.signal(signal.SIGCHLD, _sChild)


print "MAIN pid(%s)" % os.getpid()
Bus.publish(None, "log", "main pid(%s)" % os.getpid())

p1=TestProc("proc1")
p2=TestProc("proc2")
p3=TestProc("proc3")
p4=TestProc("proc4")
pr1=TestProcRx("procRx1")
pr2=TestProcRx("procRx2")

print "<< STARTING!"
Bus.publish(None, "start")

signal.signal(signal.SIGTERM, _shandler)

print ">> STARTED!"
while not _exitFlag:
    try:
        Bus.publish(None, "mswitch_pump")
    except Exception,e:
        print "*** (MAIN) Comm Exception!"
        Bus.publish(None, "log", "*** (MAIN) Comm exception: %s" % e)

print "***MAIN FINISHING"
sys.exit()
