import re
import inspect


class Listened:

    def __init__(self):
        self.__listeners = {}

    def add_listener(self, listener, pattern='\w+'):
        regex = re.compile(pattern)
        if not regex in self.__listeners:
            self.__listeners[regex] = set()

        args_spec = inspect.getargspec(listener)
        group_names = regex.groupindex.keys()
        if set(args_spec.args).issuperset(set(group_names)) or args_spec.keywords:
            self.__listeners[regex].add(listener)
        else:
            raise ValueError(
                'Pattern group names and listener attributes do not match.')

    def discard_listener(self, pattern, listener):
        regex = re.compile(pattern)
        if regex in self.__listeners:
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
