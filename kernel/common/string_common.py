from kernel.base_class.base_class import *
import xml.dom.minidom
#import xml.etree.ElementTree as etree
class StringCommon(BaseClass):

    def __init__(self,args):
        pass

    def to_unicode(self,a):
        sum = b''
        for x in a:
            if x == 'u':
                sum += b'\u'
            else:
                sum += x.encode()
        return sum