#!/usr/bin/env python
"""
    phidgets-couchdb
    
    @author: Jean-Lou Dupont
"""
import sys

try:
    import couchdb
except:
    import pynotify
    pynotify.init("phidgets-couchdb")
    n=pynotify.Notification("Phidgets Couchdb", "couchdb-python library not available", "phidgets-couchdb")
    n.set_urgency(pynotify.URGENCY_CRITICAL)
    n.show()
    sys.exit(1)

try:
    from couchdb.http import PreconditionFailed
except:
    import pynotify
    pynotify.init("phidgets-couchdb")
    n=pynotify.Notification("Phidgets Couchdb", "Unsupported couchdb-python library", "phidgets-couchdb")
    n.set_urgency(pynotify.URGENCY_CRITICAL)
    n.show()
    sys.exit(1)

import os
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
     
## Always import mswitch first
import system.mswitch as mswitch

## some config required
from agents.logger import LoggerAgent
_=LoggerAgent("phidgets-couchdb", "~/.phidgets-dbus/phidgets-couchdb.log")
_.start()

import agents.timer

from apps import app_couchdb
