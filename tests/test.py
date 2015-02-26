import os
import sys
sys.path.insert(0, 'docxxslt')

from lxml import etree
from docxxslt import DocxXsltTemplate, utils

docx_in = "tests/in.docx"
docx_out = "tests/out.docx"
xml_in = "tests/test.xml"
context = etree.parse(xml_in)

template = DocxXsltTemplate(docx_in)
template.save(filename=docx_out, context=context, logger=utils.get_logger())
