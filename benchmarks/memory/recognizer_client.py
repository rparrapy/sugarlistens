#!/usr/bin/env python

import dbus
import dbus.mainloop.glib
import gobject
gobject.threads_init()
import listened


class RecognizerClient(listened.Listened):

    """GStreamer/PocketSphinx Demo Application"""

    def __init__(self):
        """Initialize a DemoApp object"""
        listened.Listened.__init__(self)
        self.start_time = 0

        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self._bus = dbus.SessionBus()
        self._bus.add_signal_receiver(self.__final_result,
                                dbus_interface="org.sugarlabs.listens.recognizer",
                                signal_name="result_ready")

    def __final_result(self, text, start_time):
        """Insert the final result."""
        self.start_time = start_time
        self.notify_listeners(text)
