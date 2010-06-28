"""
    @author: jldupont

    Created on 2010-02-23
"""
__all__=["App"]

import os
import gobject
import gtk
from Queue import Queue, Empty

from   system.base import mdispatch
import system.mswitch as mswitch

from   system.base import mdispatch
import system.mswitch as  mswitch
       

class AppPopupMenu:
    def __init__(self, app):
        self.item_exit = gtk.MenuItem( "exit", True)
        self.item_exit.connect( 'activate', app.exit)

        self.menu = gtk.Menu()
        self.menu.append( self.item_exit)
        self.menu.show_all()

    def show_menu(self, button, time):
        self.menu.popup( None, None, None, button, time)
        

class AppIcon(object):
    
    ICON_PATH="/usr/share/icons/"
    ICON_FILE="phidgets-couchdb.png"
    
    def __init__(self):
        self.curdir=os.path.abspath( os.path.dirname(__file__) )
    
    def getIconPixBuf(self): 
        try:
            ipath=self.ICON_PATH+"/"+self.ICON_FILE
            pixbuf = gtk.gdk.pixbuf_new_from_file( ipath )
        except:
            ipath=self.curdir+"/"+self.ICON_FILE
            pixbuf = gtk.gdk.pixbuf_new_from_file( ipath )
                      
        return pixbuf.scale_simple(24,24,gtk.gdk.INTERP_BILINEAR)
        

class App(object):
    def __init__(self, app_name, time_base):
        self.app_name=app_name
        self.time_base=time_base
        self.ticks_second=1000/time_base
        
        self.popup_menu=AppPopupMenu(self)
        
        self.tray=gtk.StatusIcon()
        self.tray.set_visible(True)
        self.tray.set_tooltip("Phidgets-DBus, Couchdb")
        self.tray.connect('popup-menu', self.do_popup_menu)
        scaled_buf = AppIcon().getIconPixBuf()
        self.tray.set_from_pixbuf( scaled_buf )
        
        self.iq=Queue()
        self.isq=Queue()
        
        mswitch.subscribe(self.iq, self.isq)
        self.tick_count=0
        gobject.timeout_add(self.time_base, self.tick)           
        
    def do_popup_menu(self, status, button, time):
        self.popup_menu.show_menu(button, time)

    def exit(self, *p):
        mswitch.publish("__app__", "__quit__")
        gtk.main_quit()

    def tick(self, *_):
        """
        Performs message dispatch
        """
        
        tick_second = (self.tick_count % self.ticks_second) == 0 
        self.tick_count += 1
        
        #print "tick! ", tick_second
        
        mswitch.publish("__main__", "tick", self.ticks_second, tick_second)
        
        while True:
            try:     
                envelope=self.isq.get(False)
                quit, mtype, handled=mdispatch(self, "__main__", envelope)
                if handled==False:
                    mswitch.publish(self.__class__, "__interest__", (mtype, False, self.isq))
            except Empty:
                break
            continue            
        
        burst=5
        
        while True:
            try:     
                envelope=self.iq.get(False)
                quit, mtype, handled=mdispatch(self, "__main__", envelope)
                if handled==False:
                    mswitch.publish(self.__class__, "__interest__", (mtype, False, self.iq))
                    
                burst -= 1
                if burst == 0:
                    break
            except Empty:
                break
            
            continue

        return True

"""
_=App(TIME_BASE)
gtk.main()
"""