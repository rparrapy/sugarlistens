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

import os


class Recognizer(dbus.service.Object):

    LANGUAGE_MODEL = '/usr/share/pocketsphinx/model/lm/en_US/hub4.5000.DMP'
    ACOUSTIC_MODEL = '/usr/share/pocketsphinx/model/hmm/en_US/hub4wsj_sc_8k'
    PHONETIC_DICTIONARY = '/usr/share/pocketsphinx/model/lm/en_US/hub4.5000.dic'

    def __init__(self, dbus_conn, object_path='/org/sugarlabs/listens/recognizer'):
        dbus.service.Object.__init__(self, dbus_conn, object_path)
        self._language_model = Recognizer.LANGUAGE_MODEL
        self._acoustic_model = Recognizer.ACOUSTIC_MODEL
        self._phonetic_dictionary = Recognizer.PHONETIC_DICTIONARY
        self._language_model_param = 'lm'
        self._pipeline = None


    @dbus.service.signal('org.sugarlabs.listens.recognizer')
    def result_ready(self, text):
        pass

    @dbus.service.method('org.sugarlabs.listens.recognizer')
    def start_pipeline(self, path):
        lm = path + '/speech/en/language.DMP'
        if os.path.isfile(lm):
            self._language_model = lm
            self._language_model_param = 'lm'

        lm = path + '/speech/en/language.fsg'
        if os.path.isfile(lm):
            self._language_model = lm
            self._language_model_param = 'fsg'


        pd = path + '/speech/en/dictionary.dic'
        if os.path.isfile(pd):
            self._phonetic_dictionary = pd

        am = path + '/speech/en/'
        am_test_file = am + 'mdef'
        if os.path.isfile(am_test_file):
            self._acoustic_model = am

        if self._pipeline:
            self._pipeline.get_bus().remove_signal_watch()
            self._pipeline.set_state(gst.STATE_NULL)

        self.init_gst()

    def init_gst(self):
        """Initialize the speech components"""
        self._pipeline = gst.parse_launch('gconfaudiosrc ! audioconvert ! audioresample '
                                          +
                                          '! vader name=vad auto-threshold=true '
                                          + '! pocketsphinx name=asr ! fakesink')
        asr = self._pipeline.get_by_name('asr')
        asr.connect('partial_result', self.asr_partial_result)
        asr.connect('result', self.asr_result)

        # English Continuous
        print self._language_model
        print self._phonetic_dictionary
        asr.set_property(self._language_model_param, self._language_model)
        asr.set_property('dict', self._phonetic_dictionary)
        asr.set_property('hmm', self._acoustic_model)

        asr.set_property('configured', True)
        bus = self._pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message::application', self.application_message)
        self._pipeline.set_state(gst.STATE_PLAYING)

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
            # self._pipeline.set_state(gst.STATE_PAUSED)

    def partial_result(self, hyp, uttid):
        pass

    def final_result(self, hyp, uttid):
        """Insert the final result."""
        self.result_ready(hyp)


def start():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    session_bus = dbus.SessionBus()
    name = dbus.service.BusName(
        'org.sugarlabs.listens.recognizer', session_bus)
    daemon = Recognizer(name)


def main():
    start()
    loop = gobject.MainLoop()
    loop.run()


if __name__ == "__main__":
    main()
