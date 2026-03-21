from .lib_test_utils import *

from .lib_html import HTML


class IroiroHTMLDocument(TestCase):
    def test_empty_html(self):
        document = HTML('')
        self.eq(document.root, None)

    def test_invalid_input(self):
        with self.raises(TypeError):
            document = HTML(42)

    def test_only_doctype(self):
        document = HTML('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                        '"http://www.w3.org/TR/html4/strict.dtd">')
        self.eq(document.decl, 'DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"')

    def test_only_html_tag(self):
        document = HTML('<html></html>')
        self.ne(document.root, None)
        self.eq(document.root.name, 'html')

    def test_minimal_html_doc(self):
        document = HTML('<!DOCTYPE html><title>a</title>')
        self.eq(document.decl, 'DOCTYPE html')
        self.eq(document.root.name, 'title')
        self.eq(document.root.innerText, 'a')

    def test_small_html_doc(self):
        document = HTML('''
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <link href="style.css" rel="stylesheet" />
        <script type="text/javascript" src="main.js"></script>
        <title>Title</title>
    </head>
    <body onload="main()">
        <div id="container">text</div>
    </body>
</html>
''')
        self.eq(document.decl, 'DOCTYPE html')
        self.eq(document.root.name, 'html')
        self.eq(document.html.innerText.split(), ['Title', 'text'])

        self.eq([x.name for x in document.head.children],
                ['meta', 'link', 'script', 'title'])
        self.eq(document.head.meta.charset, 'utf-8')
        self.eq(document.head.link.href, 'style.css')
        self.eq(document.head.link.rel, 'stylesheet')
        self.eq(document.head.script.type, 'text/javascript')
        self.eq(document.head.script.src, 'main.js')
        self.eq(document.head.title.innerText, 'Title')

        self.eq(document.body.onload, 'main()')
        self.eq(document.body.innerText, 'text')
        self.eq(document.body.div.id, 'container')
        self.eq(document.body.div.innerText, 'text')

    def test_read_from_file(self):
        import io
        fake_file = io.StringIO('<html><head></head><body><div id="container"></div></body></html>')
        document = HTML(fake_file)
        self.eq(document.html.body.div.id, 'container')
