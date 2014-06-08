#!/usr/bin/env python

# Copyright (c) 2008 Carnegie Mellon University.
#
# You may modify and redistribute this file under the same terms as
# the CMU Sphinx system.  See
# http://cmusphinx.sourceforge.net/html/LICENSE for more information.

import dbus
import dbus.service
import dbus.mainloop.glib

import gobject
import pygst
pygst.require('0.10')
import gst
import time


class RecognizerDaemon(dbus.service.Object):

    def __init__(self, dbus_conn, object_path='/org/sugarlabs/listens/recognizer'):
        dbus.service.Object.__init__(self, dbus_conn, object_path)
        self.init_gst()
        self.start_time = time.time()


    @dbus.service.signal('org.sugarlabs.listens.recognizer')
    def result_ready(self, text, start_time):
        pass

    def init_gst(self):
        """Initialize the speech components"""
        self.pipeline = gst.parse_launch('gconfaudiosrc ! audioconvert ! audioresample '
                                         + '! vader name=vad auto-threshold=true '
                                         + '! pocketsphinx name=asr ! fakesink')
        asr = self.pipeline.get_by_name('asr')
        asr.connect('partial_result', self.asr_partial_result)
        asr.connect('result', self.asr_result)
        #Turtle Grammar
        # asr.set_property('lm', '/usr/share/pocketsphinx/model/lm/en/turtle.DMP')
        # asr.set_property('dict', '/usr/share/pocketsphinx/model/lm/en/turtle.dic')
        # asr.set_property('hmm', '/usr/share/pocketsphinx/model/hmm/en_US/hub4wsj_sc_8k')

        #English Continuous
        asr.set_property('lm', '/usr/share/pocketsphinx/model/lm/en_US/hub4.5000.DMP')
        asr.set_property('dict', '/usr/share/pocketsphinx/model/lm/en_US/hub4.5000.dic')
        asr.set_property('hmm', '/usr/share/pocketsphinx/model/hmm/en_US/hub4wsj_sc_8k')
        
        asr.set_property('configured', True)

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message::application', self.application_message)

        print 'Startin Pipeline'
        time.sleep(10)
        self.pipeline.set_state(gst.STATE_PLAYING)

    def asr_partial_result(self, asr, text, uttid):
        """Forward partial result signals on the bus to the main thread."""
        struct = gst.Structure('partial_result')
        struct.set_value('hyp', text)
        struct.set_value('uttid', uttid)
        asr.post_message(gst.message_new_application(asr, struct))

    def asr_result(self, asr, text, uttid):
        """Forward result signals on the bus to the main thread."""
        struct = gst.Structure('result')
        struct.set_value('hyp', text)
        struct.set_value('uttid', uttid)
        asr.post_message(gst.message_new_application(asr, struct))

    def application_message(self, bus, msg):
        """Receive application messages from the bus."""
        msgtype = msg.structure.get_name()
        if msgtype == 'partial_result':
            self.partial_result(msg.structure['hyp'], msg.structure['uttid'])
        elif msgtype == 'result':
            self.final_result(msg.structure['hyp'], msg.structure['uttid'])
            #self.pipeline.set_state(gst.STATE_PAUSED)

    def partial_result(self, hyp, uttid):
        """Delete any previous selection, insert text and select it."""
        pass

    def final_result(self, hyp, uttid):
        """Insert the final result."""
        # All this stuff appears as one single action
        print "Result: " + hyp
        self.result_ready(hyp, self.start_time)


def start():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    session_bus = dbus.SessionBus()
    name = dbus.service.BusName('org.sugarlabs.listens.recognizer', session_bus)
    daemon = RecognizerDaemon(name)


def main():
    start()
    loop = gobject.MainLoop()
    loop.run()

if __name__ == "__main__":
    main()
