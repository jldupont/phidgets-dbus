#!/usr/bin/env python
"""
    phidgets-couchdb
    
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
Bus.publish(None, "%logpath", "phidgets-couchdb", "~/.phidgets-dbus/phidgets-couchdb.log")

import dbus.glib
import gobject              #@UnresolvedImport

gobject.threads_init()
dbus.glib.init_threads()

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)
     
from apps import app_couchdb
     
#Bus.debug=True

#import phidgetsdbus.api.ifk_handler    #@UnusedImport
#import phidget.ifk

