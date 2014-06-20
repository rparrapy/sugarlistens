

class Configuration(object):

    def __init__(self):
        self.language_models = {
            'en': ('/usr/share/pocketsphinx/model/lm/en_US/hub4.5000.DMP', 'lm')
        }

        self.acoustic_models = {
            'en': '/usr/share/pocketsphinx/model/hmm/en_US/hub4wsj_sc_8k'
        }

        self.phonetic_dictionaries = {
            'en': '/usr/share/pocketsphinx/model/lm/en_US/hub4.5000.dic'
        }
