import os
import sys
sys.path.insert(0, 'docxxslt')

from lxml import etree
from docxxslt import DocxTemplate, xsl

xsl.DEBUG = True

def debug(mesg):
    print mesg

def warning(mesg):
    print mesg

filename = "tests/test.docx"
context = etree.XML("""
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
""")

template = DocxTemplate(filename)
template.save(filename="x%s" % os.path.basename(filename), context=context, debug=debug, warning=warning)
