#!/usr/bin/env python
"""
    @author: Jean-Lou Dupont
"""
import os
import sys
import gtk

## For development environment
ppkg=os.path.abspath( os.getcwd() +"/phidgetsdbus")
if os.path.exists(ppkg):
    sys.path.insert(0, ppkg)

from system import *
Bus.publish(None, "%logpath", "phidgets-ifk", "~/.phidgets-dbus/phidgets-ifk.log")

import dbus.glib
import gobject              #@UnresolvedImport

gobject.threads_init()
dbus.glib.init_threads()

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)
     
from apps import app_ifk
     
#Bus.debug=True

import phidgetsdbus.api.ifk_handler    #@UnusedImport
try:
    import phidget.ifk
    phidgets_ok=True
except:
    phidgets_ok=False

if phidgets_ok:
    def hQuit(*pa):
        gtk.main_quit()
    
    Bus.subscribe("%quit", hQuit)
    
    def idle():
        Bus.publish("__idle__", "%poll")
        return True
    
    gobject.timeout_add(250, idle)
    gtk.main()

else:
    import pynotify
    pynotify.init("phidgets-ifk")
    n=pynotify.Notification("Phidgets InterfaceKit", "Phidgets library not available", "phidgets-ifk")
    n.set_urgency(pynotify.URGENCY_CRITICAL)
    n.show()
