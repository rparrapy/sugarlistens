import re
import inspect


class Listened(object):

    def __init__(self):
        self.__listeners = {}
        self.__current_index = 0
        self.__listener_index = {}

    def add_listener(self, listener, pattern='\w+'):
        regex = re.compile(pattern)
        if not regex in self.__listeners:
            self.__listeners[regex] = set()

        args_spec = inspect.getargspec(listener)
        group_names = regex.groupindex.keys()
        if set(args_spec.args).issuperset(set(group_names)) or args_spec.keywords:
            self.__listeners[regex].add(listener)
            self.__listener_index[self.__current_index] = (regex, listener)
            self.__current_index += 1
            return self.__current_index - 1
        else:
            raise ValueError(
                'Pattern group names and listener attributes do not match.')

    def discard_listeners(self, pattern):
        regex = re.compile(pattern)
        if regex in self.__listeners:
            self.__listeners.pop(regex, None)

    def remove_listener(self, listener_id):
        if listener_id in self.__listener_index:
            regex, listener = self.__listener_index.pop(listener_id)
            self.__listeners[regex].discard(listener)

    def notify_listeners(self, text):
        for regex, listeners in self.__listeners.iteritems():
            match = regex.match(text)
            if match:
                for listener in listeners:
                    # raw mode
                    if regex.pattern == '\w+':
                        listener(text)
                    else:
                        listener(text, regex.pattern, **match.groupdict())
