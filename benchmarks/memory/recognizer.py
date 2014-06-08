#!/usr/bin/env python

# Copyright (c) 2008 Carnegie Mellon University.
#
# You may modify and redistribute this file under the same terms as
# the CMU Sphinx system.  See
# http://cmusphinx.sourceforge.net/html/LICENSE for more information.

import gobject
import pygst
pygst.require('0.10')
gobject.threads_init()
import gst
import listened
import time


class Recognizer(listened.Listened):

    """GStreamer/PocketSphinx Demo Application"""

    def __init__(self):
        """Initialize a DemoApp object"""
        listened.Listened.__init__(self)
        self.init_gst()
        self.start_time = time.time()

    def init_gst(self):
        """Initialize the speech components"""
        self.pipeline = gst.parse_launch('gconfaudiosrc ! audioconvert ! audioresample '
                                         +
                                         '! vader name=vad auto-threshold=true '
                                         + '! pocketsphinx name=asr ! fakesink')
        asr = self.pipeline.get_by_name('asr')
        asr.connect('partial_result', self.asr_partial_result)
        asr.connect('result', self.asr_result)
        # Turtle Grammar
        # asr.set_property(
        #     'lm', '/usr/share/pocketsphinx/model/lm/en/turtle.DMP')
        # asr.set_property(
        #     'dict', '/usr/share/pocketsphinx/model/lm/en/turtle.dic')
        # asr.set_property(
        #     'hmm', '/usr/share/pocketsphinx/model/hmm/en_US/hub4wsj_sc_8k')

        #English Continuous
        asr.set_property('lm', '/usr/share/pocketsphinx/model/lm/en_US/hub4.5000.DMP')
        asr.set_property('dict', '/usr/share/pocketsphinx/model/lm/en_US/hub4.5000.dic')
        asr.set_property('hmm', '/usr/share/pocketsphinx/model/hmm/en_US/hub4wsj_sc_8k')

        asr.set_property('configured', True)

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message::application', self.application_message)

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

    def partial_result(self, hyp, uttid):
        pass

    def final_result(self, hyp, uttid):
        """Insert the final result."""
        # All this stuff appears as one single action
        self.notify_listeners(hyp)

    def pause_pipeline(self, widget, event):
        print "Pausing Pipeline"
        self.pipeline.set_state(gst.STATE_PAUSED)

    def start_pipeline(self, widget, event):
        print "Starting Pipeline"
        self.pipeline.set_state(gst.STATE_PLAYING)
