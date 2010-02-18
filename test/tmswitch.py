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
        print "!Printer: ", msg


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
        print "doRun (%s)" % self.name
        Bus.publish(self, "log", "starting (%s) pid(%s)" % (self.name, os.getpid()))
        while True:
            #print "tick (%s)" % self.name
            self.publish(["tick", self.name, os.getpid()])
            sleep(0.550+0.250*random.random())


class TestProcRx(ProcessClass):
    def __init__(self, name):
        ProcessClass.__init__(self, name)

    def doRun(self):
        print "doRun (%s)" % self.name
        Bus.publish(self, "log", "starting (%s) pid(%s)" % (self.name, os.getpid()))
        self.subscribe("tick")
        while True:
            try:
                msg=self.getMsg()
            except Exception,e:
                Bus.publish(self, "log", "Comm Exception: %s" % e)
                print "getMsg, exception: ", e
                break
            print "Proc(%s) receive msg: %s" % (self.name, msg)
            sleep(0.550+0.250*random.random())

 
## ============================

print "main pid: ", os.getpid()

p1=TestProc("proc1")
p2=TestProc("proc2")
p3=TestProc("proc3")
p4=TestProc("proc4")
pr1=TestProcRx("procRx1")
pr2=TestProcRx("procRx2")

print "STARTING!"
Bus.publish(None, "start")

print "STARTED!"
while True:
    try:
        Bus.publish(None, "mswitch_pump")
    except Exception,e:
        print "Comm Exception!"
        Bus.publish(None, "log", "Comm exception: %s" % e)

