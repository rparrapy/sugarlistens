#!/usr/bin/env python

# Copyright (c) 2008 Carnegie Mellon University.
#
# You may modify and redistribute this file under the same terms as
# the CMU Sphinx system.  See
# http://cmusphinx.sourceforge.net/html/LICENSE for more information.

import dbus
import dbus.service
import dbus.mainloop.glib
import lockfile
import lockfile.pidlockfile 

import gobject
import pygst
pygst.require('0.10')
gobject.threads_init()
import gst

import os
import locale
import configuration


class Recognizer(dbus.service.Object):

    def __init__(self, dbus_conn, object_path='/org/sugarlabs/listens/recognizer'):
        dbus.service.Object.__init__(self, dbus_conn, object_path)
        self._config = configuration.Configuration()
        self._language_model = self._config.language_models['en'][0]
        self._acoustic_model = self._config.acoustic_models['en']
        self._phonetic_dictionary = self._config.phonetic_dictionaries['en']
        self._language_model_param = self._config.language_models['en'][1]
        self._pipeline = None

    @dbus.service.signal('org.sugarlabs.listens.recognizer')
    def result_ready(self, text):
        pass

    @dbus.service.method('org.sugarlabs.listens.recognizer')
    def start_pipeline(self, path):
	self._set_models(path)

        if self._pipeline:
            self._pipeline.get_bus().remove_signal_watch()
            self._pipeline.set_state(gst.STATE_NULL)

        self.init_gst()

    def _set_models(self, path):
        loc = locale.getdefaultlocale()[0]
        lang = loc.split('_')[0]
        default = 'en'

        options = [loc, lang, default]
        am_lang = self._set_located_acoustic(path, options)
        lm_lang = self._set_located_language(path, options)
        dict_lang = self._set_located_dictionary(path, options)

        if not (am_lang == lm_lang and lm_lang == dict_lang):
            msg = '\nAcoustic Model: %s' % am_lang + \
                '\nLanguage Model: %s' % lm_lang + \
                '\nDictionary: %s' % dict_lang
            raise Exception(
                'Different language for models and dictionary:' + msg)

    def _set_located_acoustic(self, path, options):
        result = None
        for suffix in options:
            # Local
            prefix = path + '/speech/' + suffix + '/'
            am_test_file = prefix + 'mdef'
            if os.path.isfile(am_test_file):
                self._acoustic_model = prefix
                result = suffix.split('_')[0]
                break

            default_am = self._config.acoustic_models.get(suffix)
            if default_am:
                self._acoustic_model = default_am
                result = suffix.split('_')[0]
                break

        return result

    def _set_located_language(self, path, options):
        result = None
        for suffix in options:
            prefix = path + '/speech/' + suffix + '/'

            # Local statistical language
            lm = prefix + 'language.DMP'
            if os.path.isfile(lm):
                self._language_model = lm
                self._language_model_param = 'lm'
                result = suffix.split('_')[0]
                break

            # Local Grammar
            lm = prefix + 'language.fsg'
            if os.path.isfile(lm):
                self._language_model = lm
                self._language_model_param = 'fsg'
                result = suffix.split('_')[0]
                break

            # Default model
            default_lm = self._config.language_models.get(suffix)
            if default_lm:
                self._language_model = default_lm[0]
                self._language_model_param = default_lm[1]
                result = suffix.split('_')[0]
                break

        return result

    def _set_located_dictionary(self, path, options):
        result = None
        for suffix in options:
            prefix = path + '/speech/' + suffix + '/'
            pd = prefix + 'dictionary.dic'
            # Local dict
            if os.path.isfile(pd):
                self._phonetic_dictionary = pd
                result = suffix.split('_')[0]
                break

            # Default dict
            default_dictionary = self._config.phonetic_dictionaries.get(suffix)
            if default_dictionary:
                self._phonetic_dictionary = default_dictionary
                result = suffix.split('_')[0]
                break

        return result

    def init_gst(self):
        """Initialize the speech components"""
        self._pipeline = gst.parse_launch('gconfaudiosrc ! audioconvert ! audioresample '
                                          +
                                          '! vader name=vad auto-threshold=true '
                                          + '! pocketsphinx name=asr ! fakesink')
        asr = self._pipeline.get_by_name('asr')
        asr.connect('partial_result', self.asr_partial_result)
        asr.connect('result', self.asr_result)

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
        print hyp
        self.result_ready(hyp)


def start():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    session_bus = dbus.SystemBus()
    name = dbus.service.BusName(
        'org.sugarlabs.listens.recognizer', session_bus)
    daemon = Recognizer(name)


def main():
    start()
    loop = gobject.MainLoop()
    loop.run()

if __name__ == "__main__":
    pidfile = lockfile.pidlockfile.PIDLockFile("/tmp/sugarlistens.pid")
    pidfile.acquire()
    main()
    pidfile.release()
