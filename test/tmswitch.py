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

    def doRun(self):
        print "TestProc.doRun (%s)" % self.name
        Bus.publish(self, "log", "starting (%s) pid(%s)" % (self.name, os.getpid()))
        try:
            while True:
                #print "tick (%s)" % self.name
                self.publish(["tick", self.name, os.getpid()])
                sleep(2.550+0.250*random.random())
                msg=self.getMsg(block=True, timeout=0.1)
        except Exception,e:
            print "Exiting (%s)" % self.name
            Bus.publish(self, "log", "Exiting (%s)" % e)
            Bus.publish(self, "shutdown")


class TestProcRx(ProcessClass):
    def __init__(self, name):
        ProcessClass.__init__(self, name)

    def doRun(self):
        import signal
        import sys
        
        global _exitFlag
        _exitFlag = False
        
        def _term(signum, _):
            print "_term(%s), pid(%s)" % (signum, os.getpid())
            global _exitFlag
            _exitFlag=True
            
        signal.signal(signal.SIGTERM, _term)
        signal.signal(signal.SIGPIPE, _term)
        
        print "TestProcRx.doRun (%s) pid(%s)" % (self.name, os.getpid())
        Bus.publish(self, "log", "doRun: starting (%s) pid(%s)" % (self.name, os.getpid()))
        self.subscribe("tick")
        while not _exitFlag:
            try:
                msg=self.getMsg(block=True, timeout=0.1)
            except Exception,e:
                Bus.publish(self, "log", "Comm Exception: %s" % e)
                Bus.publish(self, "shutdown")
                print "getMsg, exception: ", e
                break
            if msg is not None:
                print "Proc(%s) receive msg: %s" % (self.name, msg)
            sleep(0.01)

 
## ==============================================================
## ==============================================================
import signal
import sys

_exitFlag=False

def _shandler(signum, _):
    print "signal handler: ", signum
    global _exitFlag
    _exitFlag=True

    

signal.signal(signal.SIGTERM, _shandler)
#signal.signal(signal.SIGKILL, _shandler)


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

print ">> STARTED!"
while not _exitFlag:
    try:
        Bus.publish(None, "mswitch_pump")
    except Exception,e:
        print "Comm Exception!"
        Bus.publish(None, "log", "Comm exception: %s" % e)

print "***MAIN FINISHING"
sys.exit()
