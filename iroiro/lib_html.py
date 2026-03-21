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
        self.roots = []
        self.stack = []

        if hasattr(source, 'read') and callable(source.read):
            self.feed(source.read())
        elif isinstance(source, str):
            self.feed(source)
        else:
            raise TypeError('Unrecognized source:', repr(source))

    @property
    def root(self):
        if self.roots:
            return self.roots[0]

    def __getattr__(self, name):
        for root in self.roots:
            if name == root.name:
                return root

        for root in self.roots:
            try:
                return getattr(root, name)
            except AttributeError:
                pass

        raise AttributeError(name)

    def handle_decl(self, decl):
        self.decl = decl

    def handle_comment(self, data):
        pass

    def handle_starttag(self, tag, attrs):
        elem = HTMLElement(tag, attrs)

        if not self.stack:
            self.roots.append(elem)

        if self.stack:
            self.stack[-1].append(elem)

        if tag not in self_closing_tags:
            self.stack.append(elem)

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
        self.childnodes = []

    def __repr__(self):
        if self.attrs:
            attr = ' ' + repr(self.attrs)
        else:
            attr = ''
        if self.name in self_closing_tags:
            return f'<{self.name}{attr}>'

        return (f'<{self.name}{attr}>' +
                ''.join(child if isinstance(child, str) else repr(child) for child in self.childnodes) +
                f'</{self.name}>')

    @property
    def tagname(self):
        return self.name

    @property
    def classlist(self):
        return self.attrs.get('class', '').split()

    @property
    def dataset(self):
        # TODO
        return []

    @property
    def children(self):
        return [child
                for child in self.childnodes
                if not isinstance(child, str)
                ]

    @property
    def innerText(self):
        # TODO
        return ' '.join(child if isinstance(child, str) else child.innerText
                       for child in self.childnodes)

    def __getattr__(self, name):
        if name in self.attrs:
            return self.attrs[name]

        for child in self.children:
            if child.name == name:
                return child

        raise AttributeError(name)

    def append(self, elem):
        self.childnodes.append(elem)
