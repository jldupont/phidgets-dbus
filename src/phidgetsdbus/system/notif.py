"""
    @author: jldupont

    Created on Jun 28, 2010
"""
__all__=["show"]

import pynotify

def show(app_name, msg, icon=None):
    pynotify.init(app_name)
    n=pynotify.Notification(app_name, msg, icon)
    n.set_urgency(pynotify.URGENCY_CRITICAL)
    n.show()
