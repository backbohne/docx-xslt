from . import engines, package

__version__ = '0.0.1'


def debug():
    pass


def warning():
    pass


class DocxTemplate(object):
    """Docx template renderer"""

    main_document = 'word/document.xml'

    def __init__(self, filename):
        self.package = package.Package(filename)
        self.package.read()

    def save(self, filename=None, **kwargs):
        filename = filename or self.package.filename
        engine = kwargs.pop('engine', engines.DefaultEngine)
        context = kwargs.pop('context')
        debug_callback = kwargs.pop('debug', debug)
        warning_callback = kwargs.pop('warning', warning)

        # read docx XML string
        xml = self.package.get(self.main_document)

        # render XML
        xml = engine(debug=debug_callback, warning=warning_callback).render(xml, context)

        # write docx document
        self.package.update(self.main_document, xml)
        self.package.write(filename)
