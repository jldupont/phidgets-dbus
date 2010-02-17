#!/usr/bin/env python
"""
    @author: Jean-Lou Dupont
"""
import sys
import os

ppkg=os.path.abspath( os.getcwd() +"/../src")
sys.path.insert(0, ppkg)

from multiprocessing import Process

class TestProc(Process):
    def __init__(self, name=None):
        Process.__init__(self)
        self.name=name
        
    def run(self):
        pass
