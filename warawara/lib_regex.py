import re


__all__ = ['rere']


class rere:
    def __init__(self, text):
        self.text = text
        self.cache = None

    def search(self, pattern, flags=0):
        self.cache = re.search(pattern, self.text, flags=flags)
        return self.cache

    def match(self, pattern, flags=0):
        self.cache = re.match(pattern, self.text, flags=flags)
        return self.cache

    def fullmatch(self, pattern, flags=0):
        self.cache = re.fullmatch(pattern, self.text, flags=flags)
        return self.cache

    def split(self, pattern, maxsplit=0, flags=0):
        return re.split(pattern, self.text, maxsplit=maxsplit, flags=flags)

    def findall(self, pattern, flags=0):
        return re.findall(pattern, self.text, flags=flags)

    def __getattr__(self, attr):
        if hasattr(re, attr):
            result = getattr(re, attr)
        return getattr(self.cache, attr)

    def sub(self, pattern, repl):
        return re.sub(pattern, repl, self.text)
