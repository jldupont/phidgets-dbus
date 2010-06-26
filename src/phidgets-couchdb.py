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

import dbus.glib
import gobject

gobject.threads_init()
dbus.glib.init_threads()

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)
     
import system.mswitch as mswitch
import agents.logger
mswitch.publish("__main__", "loginit", "phidgets-couchdb", "~/.phidgets-dbus/phidgets-couchdb.log")

import agents.timer

from apps import app_couchdb
