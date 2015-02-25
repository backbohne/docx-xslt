from .namespaces import NAMESPACES


class fldChar(object):
    namespaces = NAMESPACES

    def __init__(self, node):
        self.node = node

    @classmethod
    def find(cls, root):
        xpath = './/w:p/w:r/w:fldChar[@w:fldCharType="begin"]'
        return [cls(node) for node in root.xpath(xpath, namespaces=cls.namespaces)]

    @property
    def name(self):
        n = self.node.xpath('.//w:ffData/w:name', namespaces=self.namespaces)
        name = None
        if n:
            name = n[0].attrib['{%s}val' % self.namespaces['w']]
        return name or self.default

    @property
    def enabled(self):
        return len(self.node.xpath('.//w:ffData/w:enabled', namespaces=self.namespaces)) > 0

    @property
    def default(self):
        n = self.node.xpath('.//w:ffData/w:textInput/w:default', namespaces=self.namespaces)
        if n:
            return n[0].attrib['{%s}val' % self.namespaces['w']]

    def __unicode__(self):
        return u"<%s default=%s %s>" % (self.name, self.default, self.text)

    def clean(self):
        paragraph = self.paragraph
        paragraph.getparent().remove(paragraph)

    def fix(self):
        run = self._get_text_run()
        paragraph = self.paragraph
        self.clean()
        paragraph.append(run)

    @property
    def _text_run(self):
        end = self.paragraph.xpath('.//w:r/w:fldChar[@w:fldCharType="end"]', namespaces=self.namespaces)[0]
        return end.getparent().getprevious()

    @property
    def text(self):
        return self._text_run[1].text

    @text.setter
    def text(self, value):
        self._text_run[1].text = unicode(value)

    @property
    def run(self):
        return self.node.getparent()

    @property
    def paragraph(self):
        return self.run.getparent()

    def remove(self):
        paragraph = self.paragraph
        paragraph.getparent().remove(paragraph)


class fldSimple(fldChar):
    @classmethod
    def find(cls, root):
        xpath = './/w:p/w:fldSimple'
        return [cls(node) for node in root.xpath(xpath, namespaces=cls.namespaces)]

    @property
    def instr(self):
        return self.node.attrib['{%s}instr' % self.namespaces['w']]

    @property
    def name(self):
        return self.instr.split()[1]

    @property
    def enabled(self):
        return True

    @property
    def default(self):
        return self.instr.split()[3]

    def __unicode__(self):
        return u"<%s default=%s %s>" % (self.name, self.default, self.text)

    @property
    def text(self):
        return self.node[0].text

    @text.setter
    def text(self, value):
        self.node[0].text = value

    @property
    def run(self):
        pass

    @property
    def paragraph(self):
        return self.node.getparent()
