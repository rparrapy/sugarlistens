import listened
import dbus


class RecognitionHelper(listened.Listened):

    def __init__(self, path):
        listened.Listened.__init__(self)
        self._path = path
        self._bus = dbus.SessionBus()
        self._bus.add_signal_receiver(self.__final_result,
                                      dbus_interface='org.sugarlabs.listens.recognizer',
                                      signal_name='result_ready')

        self._recognizer_service = self._bus.get_object(
            'org.sugarlabs.listens.recognizer',
            '/org/sugarlabs/listens/recognizer')

        print path

    def listen(self, listener):
        self.add_listener(listener)

    def listen_to(self, pattern, listener):
        self.add_listener(listener, pattern)

    def start_listening(self):
        start_pipeline = self._recognizer_service.get_dbus_method(
            'start_pipeline',
            'org.sugarlabs.listens.recognizer')
        start_pipeline(self._path)
        pass

    def stop_listening(self):
        pass

    def __final_result(self, text):
        """Insert the final result."""
        self.notify_listeners(text)
