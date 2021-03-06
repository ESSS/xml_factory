from __future__ import unicode_literals
from ._pretty_xml import WritePrettyXMLElement
from io import StringIO
from xml.etree import ElementTree
import six
import sys



#===================================================================================================
# XmlFactory
#===================================================================================================
class XmlFactory(object):
    '''
    Fast and easy XML creation class.

    This class provides a simple a fast way of creating XML files in Python. It tries to deduce as
    much information as possible, creating intermediate elements as necessary.

    Example:
        xml = XmlFactory('root')

        xml['alpha/bravo/charlie'] # Create intermediate nodes
        xml['alpha/bravo.one'] # Create attribute on "alpha/bravo" tag
        xml['alpha/delta'] = 'XXX' # Create delta tag with text

        xml.Write('filename.xml') # Always write with a pretty XML format
    '''

    def __init__(self, root_element):
        '''
        :param str|Element root_element:
        '''
        if isinstance(root_element, six.string_types):
            self.root = ElementTree.Element(root_element)
        elif isinstance(root_element, ElementTree.Element):
            self.root = root_element
        else:
            raise TypeError("Unknown root_element parameter type: %s" % type(root_element))


    def __setitem__(self, name, value):
        '''
        Create a new element or attribute:

        :param unicode name:
            A XML path including or not an attribute definition

        :param unicode value:
            The value to associate with the element or attribute

        :returns Element:
            Returns the element created.
            If setting an attribute value, returns the owner element.

        @examples:
            xml['alpha/bravo'] = 'XXX' # Create bravo tag with 'XXX' as text contents
            xml['alpha.class'] = 'CLS' # Create alpha with the attribute class='CLS'
        '''
        if '@' in name:
            element_name, attr_name = name.rsplit('@')
            result = self._ObtainElement(element_name)
            result.attrib[attr_name] = str(value)
        else:
            result = self._ObtainElement(name)
            result.text = six.text_type(value)
        return XmlFactory(result)


    def __getitem__(self, name):
        '''
        Create and returns xml element.

        :param unicode name:
            A XML path including or not an attribute definition.

        :rtype: Element
        :returns:
            Returns the element created.
        '''
        assert '@' not in name, 'The "at" (@) is used for attribute definitions'
        result = self._ObtainElement(name)
        return XmlFactory(result)


    def _ObtainElement(self, name):
        '''
        Create and returns a xml element with the given name.

        :param unicode name:
            A XML path including. Each sub-client tag separated by a slash.
            If any of the parts ends with a "+" it creates a new sub-element in that part even if
            it already exists.
        '''
        parent = self.root
        if name == '':
            # On Python 2.7 parent.find('') returns None instead of the parent itself
            result = parent
        else:
            parts = name.split('/')
            for i_part in parts:
                if i_part.endswith('+'):
                    i_part = i_part[:-1]
                    result = ElementTree.SubElement(parent, i_part)
                else:
                    result = parent.find(i_part)
                    if result is None:
                        result = ElementTree.SubElement(parent, i_part)
                parent = result
        return result


    def Print(self, oss=sys.stdout, xml_header=False):
        '''
        Prints the resulting XML in the stdout or the given output stream.

        :type oss: file-like object | None
        :param oss:
            A file-like object where to write the XML output. If None, writes the output in the
            stdout.
        '''
        if xml_header:
            oss.write('<?xml version="1.0" ?>\n')
        WritePrettyXMLElement(oss, self.root)


    def Write(self, filename, xml_header=False):
        '''
        Writes the XML in a file with the given filename.

        :param unicode filename:
            A filename.
        '''
        with open(filename, 'w') as f:
            f.write(self.GetContents(xml_header=xml_header))


    def GetContents(self, xml_header=False):
        '''
        Returns the resulting XML.

        :return unicode:
        '''
        oss = StringIO()
        self.Print(oss, xml_header=xml_header)
        return oss.getvalue()
