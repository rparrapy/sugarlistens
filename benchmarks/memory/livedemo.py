#!/usr/bin/env python

# Copyright (c) 2008 Carnegie Mellon University.
#
# You may modify and redistribute this file under the same terms as
# the CMU Sphinx system.  See
# http://cmusphinx.sourceforge.net/html/LICENSE for more information.

import pygtk
pygtk.require('2.0')
import gtk

import gobject
gobject.threads_init()

import recognizer
import time


class DemoApp(object):

    """GStreamer/PocketSphinx Demo Application"""

    def __init__(self):
        """Initialize a DemoApp object"""
        self.init_gui()
        self.__recognizer = recognizer.Recognizer()
        self.__recognizer.add_listener(self.final_result)

    def init_gui(self):
        """Initialize the GUI components"""
        self.window = gtk.Window()
        self.window.connect("delete-event", gtk.main_quit)
        self.window.set_default_size(400, 200)
        self.window.set_border_width(10)
        vbox = gtk.VBox()
        self.textbuf = gtk.TextBuffer()
        self.text = gtk.TextView(self.textbuf)
        self.text.set_wrap_mode(gtk.WRAP_WORD)
        vbox.pack_start(self.text)
        self.button = gtk.ToggleButton("Speak")
        self.button.connect('clicked', self.button_clicked)
        vbox.pack_start(self.button, False, False, 5)
        self.window.add(vbox)
        self.window.show_all()
        print 'Show window!'

    def final_result(self, text):
        """Insert the final result."""
        # All this stuff appears as one single action
        self.textbuf.begin_user_action()
        delta = time.time() - self.__recognizer.start_time
        self.textbuf.set_text(str(delta))
        self.textbuf.end_user_action()

    def button_clicked(self, button):
        """Handle button presses."""
        if button.get_active():
            button.set_label("Stop")
            self.__recognizer.start_pipeline()
        else:
            button.set_label("Speak")
            self.__recognizer.pause_pipeline()

app = DemoApp()
gtk.main()
