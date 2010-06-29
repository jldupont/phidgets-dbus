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
DEBUG=True

import sys
import os
import gtk
import dbus.glib
import gobject

## dev environment
cpath=os.path.dirname(__file__)
ppkg=os.path.abspath( os.path.join(cpath, "phidgetsdbus"))
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
     
import system.base as base
base.debug=DEBUG
     
## Always import mswitch first
import system.mswitch as mswitch

## list of agents required to sync
##  NOTE: naming isn't important, only count is
AGENTS=["Logger", "Couchdb", "Notifier"]

from agents.sync import SyncAgent
_sa=SyncAgent(AGENTS)
_sa.start()

## some config required

from agents.timer import TimerAgent
_ta=TimerAgent(FREQ)
_ta.start()

from agents.notifier import NotifierAgent
_na=NotifierAgent(APP, ICON_NAME)
_na.start()

from agents.couchdb_agent import CouchdbAgent

from agents.logger import LoggerAgent
_la=LoggerAgent(APP, LOGPATH)
_la.config_params(CouchdbAgent, CouchdbAgent.C_LOGPARAMS)
_la.start()

from apps.app_couchdb import App
_app=App(APP, TIME_BASE)

gtk.main()
