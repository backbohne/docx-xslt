"""
from lxml import etree

context = etree.XML("
<data>
    <name>Testkunde ABC</name>
       <products>
           <product>
               <name>Produkt 1</name>
               <price>100</price>
           </product>
           <product>
               <name>Produkt 2</name>
               <price>150</price>
        </product>
           <product>
               <name>Produkt 3</name>
               <price>200</price>
        </product>
           <product>
               <name>Produkt 4</name>
               <price>500</price>
        </product>
    </products>
</data>
")

template = DocxTemplate(filename)
template.save(context=context)
"""

from . import engines, package


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

        # read docx XML string
        xml = self.package.get(self.main_document)

        # render XML
        xml = engine(debug=debug, warning=warning).render(xml, context)

        # write docx document
        self.package.update(self.main_document, xml)
        self.package.write(filename)
