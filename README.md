# docx-xslt

*docx-xslt* is a Python library for adding XSL transformation for Microsoft Word .docx files without XML or XSLT
coding.

The module uses Word *meta text* which has been formated with a specific character template called `XSL`, add XSL
code and applies XSL transformation with the XML context.

The meta text has the following syntax:

```
 <meta text>        ::= <command list>
 <command list>     ::= <command expr> | <command list>
 <command expr>     ::= 'xsl' ':' <context expr> <xsl command expr> <xsl option expr>
 <context expr>     ::= ':' <context type> | 
 <context type>     ::= 'body' | 'p0' | 'p' | 'r' | 't' | 'tbl' | 'tr' | 'tc'
 <xsl command expr> ::= <meta command> | <xsl command>
 <meta command>     ::= 'meta' <meta sub command>
 <meta sub command> ::= 'up' | 'prev' | 'next' | 'cloneprev' | 'clonenext' | 'delete'
 <xsl command>      ::= 'for-each' | 'choose' | 'when' | 'otherwise' | 'if' | 'sort' | 'value-of' | 'text'
 <xsl option expr>  ::= <text> | <xsl option name> '=' <xsl option value>
 <text>             ::= ...
 <xsl option name>  ::= 'select' | 'test'
 <xsl option value> ::=  xpath expr
```

To insert a list of a product names, just add `xsl:for-each select=.//products/* xsl:t:value-of select=name` and format the text with the `XSL` template.

```python
from lxml import etree
from docxxslt import DocxXsltTemplate

context = etree.parse("products.xml")
template = DocxXsltTemplate(filename)
template.save(context=context)
```

## Installing

```bash
pip install docx-xslt
```
