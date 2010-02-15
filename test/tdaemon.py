#!/usr/bin/env python
"""
    @author: Jean-Lou Dupont
"""
import sys
import os
import time

ppkg=os.path.abspath( os.getcwd() +"/../src")
sys.path.insert(0, ppkg)

from phidgetsdbus.daemon.runner import DaemonRunner

class MyApp(object):
    def __init__(self):
        self.stdin_path="/dev/null"
        self.stdout_path="/dev/null"
        self.stderr_path="/dev/null"
        self.pidfile_path="/var/run/tdaemon"
        self.pidfile_timeout=2

    def run(self):
        while True:
            time.sleep(1)


        

app=MyApp()
dr=DaemonRunner(app)

dr.parse_args(sys.argv)
dr.do_action()


