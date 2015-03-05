import re
import os
from lxml import etree

from .utils import *
from .namespaces import NAMESPACES


CONTEXTS = ('root', 'body', 'p0', 'p', 'r', 't', 'tbl', 'tr', 'tc')
META_COMMANDS = ('up', 'prev', 'next', 'cloneprev', 'clonenext', 'delete')
DEFAULT_CMD_TO_CONTEXT_MAPPING = {
    'for-each':  ('w', 'p'),        # xsl::for-each select=...
    'choose':    ('w', 'p'),        # xsl::choose
    'when':      ('xsl', 'choose'), # xsl::when test=...
    'otherwise': ('xsl', 'choose'), # xsl::otherwise
    'if':        ('w', 'p'),        # xsl::if test=...
    'sort':      ('w', 'p'),        # xsl::sort select=...
    'value-of':  ('w', 't'),        # xsl::value-of select=...
    'text':      ('w', 't'),        # xsl::text ...
    'meta':      ('w', 'r'),        # xsl::meta up|prev|next|cloneprev|clonenext|delete
}


class XslError(Exception):
    pass


class ParseError(XslError):
    pass


class ElementNotFound(XslError):
    pass


class XslCommand(object):
    """Object thats represents a single XSL command"""

    def __init__(self, xsl):
        self.parse(xsl)

    def __str__(self):
        return "xsl:%s:%s %s" % (self.context or '', self.cmd, self.meta_commands or self.text or self.options)

    def parse(self, xsl='text'):
        """
        TODO: add double-quoted string literals that allows for escaped double quotes
        https://gist.github.com/prathe/2439752 or
        http://www.metaltoad.com/blog/regex-quoted-string-escapable-quotes
        """

        try:
            cmd_text, option_text = xsl.split(None, 1)
        except ValueError:
            cmd_text = xsl
            option_text = ''

        try:
            context, cmd = cmd_text.strip().lower().split(':', 1)
        except ValueError:
            cmd = cmd_text.lower()
            context = None

        if not cmd in DEFAULT_CMD_TO_CONTEXT_MAPPING:
            raise ParseError("unknown command %s" % cmd)

        if context and not context in CONTEXTS:
            raise ParseError("unknown context %s" % context)

        self.context = context
        self.cmd = cmd
        self.text = None
        self.meta_commands = []
        self.options = {}

        try:
            if cmd in ('choose', 'text', 'meta'):
                raise ValueError()
            option_name, expr = option_text.split('=', 1)
            option_name = option_name.strip().lower()
            expr = unescape(expr).strip("'").strip('"').strip()
            self.options = {option_name: expr}

        except ValueError:
            text = unescape(option_text)

            if cmd == 'meta':
                for mc in filter(lambda c: c, map(lambda c: c.strip(), text.lower().split(';'))):
                    if mc in META_COMMANDS:
                        # store in stack order
                        self.meta_commands = [mc] + self.meta_commands
                    else:
                        raise ParseError("unknown meta command %s" % self.text)

            else:
                self.text = text


class XslElement(LoggerMixin):
    """List thats represents a XSL command set"""

    namespaces = NAMESPACES
    w_ns = 'w'
    xsl_ns = 'xsl'

    def __init__(self, r, logger=None):
        self.commands = []
        self.run = r
        self.parse()
        self.logger = logger

    def parse(self):
        def remove_junk(xsl):
            xsl = unidecode(xsl)
            xsl = re.sub(r"^[\t\s]*", "", xsl, re.DOTALL|re.MULTILINE|re.UNICODE)
            xsl = os.linesep.join([s for s in xsl.splitlines() if s])
            xsl = re.sub(r"\n", "", xsl, re.DOTALL|re.MULTILINE|re.UNICODE)
            xsl = re.sub(r"\r", "", xsl, re.DOTALL|re.MULTILINE|re.UNICODE)
            xsl = re.sub(r"xsl\s*:", "xsl:", xsl, re.DOTALL|re.MULTILINE|re.UNICODE|re.IGNORECASE)
            xsl = re.sub(r"xsl:\s*", "xsl:", xsl, re.DOTALL|re.MULTILINE|re.UNICODE|re.IGNORECASE)
            return xsl

        t = self.run.xpath('.//w:t',  namespaces=self.namespaces)[0]
        text = remove_junk(unicode(t.text))

        for xsl in filter(lambda xsl: xsl.strip(), text.split('xsl:')):
            try:
                cmd = XslCommand(xsl)
            except ParseError as e:
                self.error("%s ignore invalid XSL %s: %s" % (self.__class__.__name__, xsl, e))
            else:
                # store commands in stack order
                self.commands = [cmd] + self.commands

        # clean w:t
        t.text = ''

    @property
    def xsl(self):
        """Returns content as XSL text"""
        return ' '.join([str(cmd) for cmd in self.commands])

    def __str__(self):
        return self.xsl

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.xsl)

    def hascontext(self, e, ns, context):
        return str(e.tag) == '{%s}%s' % (self.namespaces[ns], context)

    def getcontext(self, e, ns, context, raise_if_not_found=True):
        f = e
        while not self.hascontext(f, ns, context):
            f = f.getparent()
            if f is None:
                break
        if not f is None:
            return f
        elif raise_if_not_found:
            raise ElementNotFound("could not find %s:%s element in %s" % (ns, context, e))

    def root(self, e):
        """Returns root node"""
        while not e.getparent() is None:
            e = e.getparent()
        return e

    def body(self, e):
        """Returns top level w:body node"""
        return self.getcontext(e, self.w_ns, 'body')

    def p0(self, e):
        """Returns top level w:p node"""
        body = self.body(e)
        p = self.p(e)
        if body == p.getparent():
            return p
        else:
            raise ElementNotFound("could not find top level w:p element in %s" % e)

    def _w_x(self, e, x):
        d = self.getcontext(e, self.w_ns, x, raise_if_not_found=False)
        f = e.xpath('.//w:%s' % x,  namespaces=self.namespaces)
        if d is not None:
            return d
        elif f:
            return f[0]
        else:
            raise ElementNotFound("could not find w:%s element in %s" % (x, e))

    def t(self, e):
        """Returns w:t node"""
        return self._w_x(e, 't')

    def r(self, e):
        """Returns w:r node"""
        return self._w_x(e, 'r')

    def p(self, e):
        """Returns w:p node"""
        return self._w_x(e, 'p')

    def tc(self, e):
        """Returns w:tc node"""
        return self._w_x(e, 'tc')

    def tr(self, e):
        """Returns w:tr node"""
        return self._w_x(e, 'tr')

    def tbl(self, e):
        """Returns w:tbl node"""
        return self._w_x(e, 'tbl')

    def render(self, current):
        def append(e, qn, options={}):
            return etree.SubElement(e, qn, **options)

        def wrap(e, qn, options={}):
            f = e.makeelement(qn, options)
            p = e.getparent()
            i = p.index(e)
            p.remove(e)
            f.append(e)
            p.insert(i, f)
            return f

        def clone(e):
            return etree.fromstring(etree.tostring(e))

        def cloneprev(e):
            c = clone(e)
            p = e.getparent()
            i = p.index(e)
            if i > 0:
                i -= 1
            p.insert(i, c)
            return c

        def clonenext(e):
            c = clone(e)
            p = e.getparent()
            i = p.index(e)
            p.insert(i+1, c)
            return c

        ns, context = self.w_ns, None

        self.debug("render %s %s with %s" % (id(current), current.xpath('name()'), self))

        while self.commands:
            cmd = self.commands.pop()

            # initialize namespace and context
            if context is None and ns == self.w_ns:
                ns, context = DEFAULT_CMD_TO_CONTEXT_MAPPING.get(cmd.cmd, current.xpath('name()').split(':'))
                current = getattr(self, context)(current)
                self.debug("initialize context to %s %s" % (id(current), current.xpath('name()')))

            # switch to required context
            if cmd.context and cmd.context != context:
                current = getattr(self, cmd.context)(current)
                ns, context = current.xpath('name()').split(':')
                self.debug("changed context to %s %s" % (id(current), current.xpath('name()')))

            if cmd.cmd == 'meta':
                while cmd.meta_commands:
                    mc = cmd.meta_commands.pop()

                    if mc == 'up' and current.getparent():
                        current = current.getparent()
                        self.debug("meta up to %s %s" % (id(current), current.xpath('name()')))

                    elif mc == 'prev':
                        parent = current.getparent()
                        i = parent.index(current)
                        if i > 0:
                            current = parent[i-1]
                        self.debug("meta prev to %s %s" % (id(current), current.xpath('name()')))

                    elif mc == 'next':
                        parent = current.getparent()
                        i = parent.index(current)
                        if len(parent) > i+1:
                            current = parent[i+1]
                        self.debug("meta next to %s %s" % (id(current), current.xpath('name()')))

                    elif mc == 'cloneprev':
                        cloneprev(current)
                        self.debug("meta cloneprev from %s %s" % (id(current), current.xpath('name()')))

                    elif mc == 'clonenext':
                        clonenext(current)
                        self.debug("meta clonenext from %s %s" % (id(current), current.xpath('name()')))

                    elif mc == 'delete':
                        parent = current.getparent()
                        parent.remove(current)
                        current = parent
                        self.debug("meta delete and goto parent %s %s" % (id(current), current.xpath('name()')))

            elif cmd.cmd in ('text', 'value-of'):
                current = append(current, etree.QName(self.namespaces[self.xsl_ns], cmd.cmd), cmd.options)
                current.text = cmd.text
                self.debug("append %s %s %s" % (id(current), current.xpath('name()'), cmd))

            else:
                wrap(current, etree.QName(self.namespaces[self.xsl_ns], cmd.cmd), cmd.options)
                self.debug("wrap %s %s %s" % (id(current), current.xpath('name()'), cmd))

            # fix current namespace and context
            ns, context = current.xpath('name()').split(':')

            # clear last cmd
            cmd = None
