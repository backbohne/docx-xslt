import logging

from . import engines, package

__version__ = '1.0.4'


class DocxXsltTemplate(object):
    """Docx template renderer"""

    main_document = 'word/document.xml'

    def __init__(self, filename):
        self.package = package.Package(filename)
        self.package.read()

    def save(self, filename=None, **kwargs):
        filename = filename or self.package.filename
        engine = kwargs.pop('engine', engines.DefaultEngine)
        context = kwargs.pop('context')
        logger = kwargs.pop('logger', logging.getLogger())

        # read docx XML string
        xml = self.package.get(self.main_document)

        # render XML
        xml = engine(logger=logger).render(xml, context)

        # write docx document
        self.package.update(self.main_document, xml)
        self.package.write(filename)
