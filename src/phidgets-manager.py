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

from phidgetsdbus.system import *
Bus.publish(None, "logpath", "phidgets-manager", "~/phidgets-manager.log")

import dbus.glib
import gobject              #@UnresolvedImport

gobject.threads_init()
dbus.glib.init_threads()

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

class BusLogger(object):
    def __init__(self):
        pass
    def __call__(self, *p):
        print "BusLogger: ", p
        
#Bus.logger=BusLogger()
#Bus.debug=True

import phidgetsdbus.api     #@UnusedImport
import phidget

def idle():
    Bus.publish("__idle__", "%poll")
    return True

gobject.timeout_add(1000, idle)
loop = gobject.MainLoop()
loop.run()
