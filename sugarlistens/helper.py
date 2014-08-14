import listened
import dbus


class RecognitionHelper(listened.Listened):

    def __init__(self, path):
        listened.Listened.__init__(self)
        self._path = path
        self._bus = dbus.SystemBus()
        self._bus.add_signal_receiver(self.__final_result,
                                      dbus_interface='org.sugarlabs.listens.recognizer',
                                      signal_name='result_ready')

        self._recognizer_service = self._bus.get_object(
            'org.sugarlabs.listens.recognizer',
            '/org/sugarlabs/listens/recognizer')


    def listen(self, listener):
        return self.add_listener(listener)

    def listen_to(self, pattern, listener):
        return self.add_listener(listener, pattern)

    def start_listening(self):
        start_pipeline = self._recognizer_service.get_dbus_method(
            'start_pipeline',
            'org.sugarlabs.listens.recognizer')
        start_pipeline(self._path)

    def stop_listening(self, pattern=None):
        if pattern:
            self.discard_listeners(pattern)
        else:
            self.discard_listeners()

    def stop_pipeline(self):
        stop_pipeline = self._recognizer_service.get_dbus_method(
            'stop_pipeline',
            'org.sugarlabs.listens.recognizer')
        stop_pipeline()
    
    def resume_pipeline(self):
        resume_pipeline = self._recognizer_service.get_dbus_method(
            'resume_pipeline',
            'org.sugarlabs.listens.recognizer')
        resume_pipeline()

    def __final_result(self, text):
        """Insert the final result."""
        self.notify_listeners(text)
