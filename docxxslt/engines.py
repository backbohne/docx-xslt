from lxml import etree

from .nodes import fldChar, fldSimple
from .xsl import XslElement
from .namespaces import NAMESPACES
from .utils import *


class BaseEngine(LoggerMixin):
    """Base engine class"""

    namespaces = NAMESPACES

    def __init__(self, **kwargs):
        self.logger = kwargs.pop('logger', None)

    @property
    def xml(self):
        """Returns XML as string"""

        if getattr(self, '_root', None):
            return t2s(self.root)
        return getattr(self, '_xml', None)

    @xml.setter
    def xml(self, value):
        """Set new XML string"""

        self._xml = value
        self._root = s2t(value)

    @property
    def root(self):
        """Returns XML tree"""

        return getattr(self, '_root', None)

    @root.setter
    def root(self, value):
        """Set new XML tree"""

        self._xml = t2s(value)
        self._root = value

    def render(self, xml, context):
        """Overwrite this methode ..."""

        return xml


class XslEngine(BaseEngine):
    """Engine thats support XSL commands.

       Define a dummy style template such as 'XSL' in your Word document.
       Insert XSLT meta commands in your text and format them with the 'XSL' style.
    """

    def __init__(self, **kwargs):
        self.style = kwargs.pop('style', 'XSL')
        super(XslEngine, self).__init__(**kwargs)

    @property
    def xsl_elements(self):
        """Find all "XSL" styled runs, normalize related paragraph and returns list of XslElements"""

        def append_xsl_elements(xsl_elements, r, xsl):
            if r is not None:
                r.xpath('.//w:t',  namespaces=self.namespaces)[0].text = xsl
                xe = XslElement(r, logger=self.logger)
                xsl_elements.append(xe)
            return None, ''

        if not getattr(self, '_xsl_elements', None):
            xsl_elements = []
            for p in self.root.xpath('.//w:p', namespaces=self.namespaces):
                xsl_r, xsl = None, ''
                for r in p:
                    # find first XSL run and add all XSL meta text
                    text = ''.join(t.text for t in r.xpath('.//w:t', namespaces=self.namespaces))
                    if r.xpath('.//w:rPr/w:rStyle[@w:val="%s"]' % self.style, namespaces=self.namespaces):
                        xsl += text
                        if xsl_r is None and text:
                            xsl_r = r
                        else:
                            r.getparent().remove(r)
                    elif text:
                        xsl_r, xsl = append_xsl_elements(xsl_elements, xsl_r, xsl)
                xsl_r, xsl = append_xsl_elements(xsl_elements, xsl_r, xsl)
            self._xsl_elements = xsl_elements

        return self._xsl_elements

    def render_xsl(self, node, context):
        """Render all XSL elements"""

        for e in self.xsl_elements:
            e.render(e.run)

    def remove_style(self):
        """Remove all XSL run rStyle elements"""

        for n in self.root.xpath('.//w:rStyle[@w:val="%s"]' % self.style, namespaces=self.namespaces):
            n.getparent().remove(n)

    def render(self, xml, context, raise_on_errors=True):
        """Render xml string and apply XSLT transfomation with context"""

        if xml:
            self.xml = xml

            # render XSL
            self.render_xsl(self.root, context)

            # create root XSL sheet
            xsl_ns = self.namespaces['xsl']
            rootName = etree.QName(xsl_ns, 'stylesheet')
            root = etree.Element(rootName, nsmap={'xsl': xsl_ns})
            sheet = etree.ElementTree(root)
            template = etree.SubElement(root, etree.QName(xsl_ns, "template"), match='/')

            # put OpenOffice tree into XSLT sheet
            template.append(self.root)
            self.root = root

            # drop XSL styles
            self.remove_style()

            #self.debug(self.xml)

            try:
                # transform XSL
                xsl = etree.XSLT(self.root)
                self.root = xsl(context)

            except etree.Error as e:
                # log errors
                for l in e.error_log:
                    self.error("XSLT error at line %s col %s:" % (l.line, l.column))
                    self.error("    message: %s" % l.message)
                    self.error("    domain: %s (%d)" % (l.domain_name, l.domain))
                    self.error('    type: %s (%d)' % (l.type_name, l.type))
                    self.error('    level: %s (%d)' % (l.level_name, l.level))
                    self.error('    filename: %s' % l.filename)

                if raise_on_errors:
                    raise

            return self.xml

        else:
            return xml


class fldCharEngine(BaseEngine):
    """Engine thats supports fldChar fields with a static dictionary context"""

    def render(self, xml, context):
        if xml:
            self.xml = xml
            for node in fldChar.find(self.root):
                node.text = context.get(node.name, node.name)

            return self.xml
        else:
            return xml


# set default engine
DefaultEngine = XslEngine
