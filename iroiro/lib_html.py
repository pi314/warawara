from html.parser import HTMLParser

from .internal_utils import exporter
export, __all__ = exporter()

from .lib_math import interval


self_closing_tags = {
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img',
        'input', 'link', 'meta', 'param', 'source', 'track', 'wbr',
        }


@export
class HTML(HTMLParser):
    def __init__(self, source):
        super().__init__()

        self.decl = None
        self.root = None
        self.stack = []

        self.html = None
        self.head = None
        self.body = None

        if hasattr(source, 'read') and callable(source.read):
            self.feed(source.read())
        elif isinstance(source, str):
            self.feed(source)
        else:
            raise TypeError('Unrecognized source:', repr(source))

    def handle_decl(self, decl):
        self.decl = decl

    def handle_comment(self, data):
        pass

    def handle_starttag(self, tag, attrs):
        elem = HTMLElement(tag, attrs)
        if self.root is None:
            self.root = elem

        if self.stack:
            self.stack[-1].append(elem)

        if tag not in self_closing_tags:
            self.stack.append(elem)

        if elem.name == 'html':
            self.html = elem
        elif elem.name == 'head':
            self.head = elem
        elif elem.name == 'body':
            self.body = elem

    def handle_endtag(self, tag):
        if not self.stack:
            return

        if tag in self_closing_tags:
            return

        if self.stack[-1].name == tag:
            self.stack.pop()
            return

        for i in interval(len(self.stack) - 1, 0, close=True):
            if self.stack[i].name == tag:
                self.stack[i:] = []
                break

        if not self.stack:
            self.root = None

    def handle_data(self, data):
        d = data.strip()
        # TODO
        if not d:
            return

        if self.stack:
            self.stack[-1].append(d)


class HTMLElement:
    def __init__(self, name, attrs):
        self.name = name
        self.attrs = dict(attrs)
        self.children = []

    @property
    def tagname(self):
        return self.name

    @property
    def classlist(self):
        # TODO
        return []

    @property
    def dataset(self):
        # TODO
        return []

    @property
    def innerText(self):
        # TODO
        return ' '.join(child if isinstance(child, str) else child.innerText
                       for child in self.children)

    def append(self, elem):
        self.children.append(elem)

    def __getattr__(self, name):
        if name in self.attrs:
            return self.attrs[name]

        for child in self.children:
            if child.name == name:
                return child

        raise AttributeError(name)
