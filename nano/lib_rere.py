import re


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


def selftest():
    from . import lib_selftest
    EXPECT_EQ = lib_selftest.EXPECT_EQ

    rec = rere('nano sized tools')

    m = rec.match(r'^(\w+) (\w+)$')
    EXPECT_EQ(m, None)

    m = rec.match(r'^(\w+) (\w+) (\w+)$')
    EXPECT_EQ(m.groups(), ('nano', 'sized', 'tools'))
    EXPECT_EQ(m.group(2), 'sized')

    EXPECT_EQ(rec.sub(r'sized', 'SIZED'), 'nano SIZED tools')
