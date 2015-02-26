import sys
import logging
from lxml import etree


try:
    from xml.sax.saxutils import unescape
except ImportError:
    from django.utils.html_parser import HTMLParser
    def unescape(text):
        return HTMLParser().unescape(text)


try:
    from unidecode import unidecode
except ImportError:
    print "please install python unidecode"
    raise


def t2s(t):
    return etree.tostring(t, pretty_print=True, encoding='utf-8')


def s2t(s):
    parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
    return etree.fromstring(bytes(bytearray(s)), parser=parser)


class LoggerMixin(object):
    def debug(self, mesg):
        logger = getattr(self, 'logger', None)
        if logger:
            logger.debug(mesg)

    def error(self, mesg):
        logger = getattr(self, 'logger', None)
        if logger:
            logger.error(mesg)


def get_logger(level=logging.DEBUG):
    logger = logging.getLogger()
    logger.setLevel(level)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger
