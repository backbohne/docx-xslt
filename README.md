# docx-xslt

*docx-xslt* is a Python library for adding XSL transformation for Microsoft Word .docx files.

The module uses Word "meta text" which has been formated with a specific character template called `XSL`, add XSL
code and applies XSL transformation with the XML context.

The meta text has the following syntax:

* meta text:		XSL-COMMANDS
* XSL-COMMANDS:		XSL-COMMAND XSL-COMMAND ...
* XSL-COMMAND:		xsl:[CONTEXT:]COMMAND OPTIONS
* CONTEXT:		body | p0 | p | r | t | tbl | tr | tc
* COMMAND:		META-COMMAND | XSL-COMMAND
* META-COMMAND:		meta META-SUB-COMMAND
* META-SUB-COMMAND:	up | prev | next | cloneprev | clonenext | delete
* XSL-COMMAND:		for-each | choose | when | otherwise | if | sort | value-of | text
* OPTIONS:		TEXT | OPTION-NAME=OPTION-TEXT
* TEXT:			text
* OPTION-NAME:		select | test
* OPTION-TEXT:          xpath text

To insert a list of a product names, add `xsl:p:for-each select=.//products/* xsl:t:value-of select=name` and format the text with the `XSL` template.

```python
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
```
