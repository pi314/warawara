import re


__all__ = ['rere']


class rere:
    def __init__(self, text):
        self.text = text
        self.cache = None

    def match(self, pattern):
        self.cache = re.match(pattern, self.text)
        return self.cache

    def __getattr__(self, attr):
        return getattr(self.cache, attr)

    def sub(self, pattern, repl):
        return re.sub(pattern, repl, self.text)
