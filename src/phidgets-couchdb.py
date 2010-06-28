#!/usr/bin/env python
"""
    phidgets-couchdb
    
    @author: Jean-Lou Dupont
"""

APP="Phidgets Couchdb"
ICON_NAME="phidgets-couchdb"
LOGPATH="~/.phidgets-dbus/phidgets-couchdb.log"
TIME_BASE=250  ##milliseconds
FREQ=1000/TIME_BASE

import sys
import os
import gtk
import dbus.glib
import gobject

ppkg=os.path.abspath( os.getcwd() +"/phidgetsdbus")
if os.path.exists(ppkg):
    sys.path.insert(0, ppkg)

try:
    import couchdb
except:
    import system.notif as notif
    notif.show(APP, "couchdb-python library not available", ICON_NAME)
    sys.exit(1)

try:
    from couchdb.http import PreconditionFailed
except:
    import system.notif as notif
    notif.show(APP, "Unsupported couchdb-python library", ICON_NAME)
    sys.exit(1)


gobject.threads_init()
dbus.glib.init_threads()

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)
     
## Always import mswitch first
import system.mswitch as mswitch

## list of agents required to sync
##  NOTE: naming isn't important, only count is
AGENTS=["Logger", "Couchdb", "Notifier"]

from agents.sync import SyncAgent
_sa=SyncAgent(AGENTS)
_sa.start()

## some config required
from agents.logger import LoggerAgent
_la=LoggerAgent(APP, LOGPATH)
_la.start()

from agents.timer import TimerAgent
_ta=TimerAgent(FREQ)
_ta.start()

from agents.notifier import NotifierAgent
_na=NotifierAgent(APP)
_na.start()

import agents.couchdb_agent

from apps.app_couchdb import App
_app=App(APP, TIME_BASE)

gtk.main()
