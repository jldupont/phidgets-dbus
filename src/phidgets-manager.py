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
Bus.publish(None, "%logpath", "phidgets-manager", "~/.phidgets-dbus/phidgets-manager.log")

import dbus.glib
import gobject              #@UnresolvedImport

gobject.threads_init()
dbus.glib.init_threads()

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)
     
from apps import app_manager
     
#Bus.debug=True

import phidgetsdbus.api.manager_handler #@UnusedImport
try:
    import phidget.manager
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
    
    gobject.timeout_add(1000, idle)
    gtk.main()

else:
    import pynotify
    pynotify.init("phidgets-manager")
    n=pynotify.Notification("Phidgets Manager", "Phidgets library not available", "phidgets-manager")
    n.set_urgency(pynotify.URGENCY_CRITICAL)
    n.show()
