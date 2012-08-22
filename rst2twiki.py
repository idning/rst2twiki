#!/usr/bin/env python
#copy from : http://code.google.com/p/rst2trac/source/browse/trunk/rst2wiki.py?r=4

import sys
from docutils.nodes import SparseNodeVisitor, GenericNodeVisitor, paragraph, title_reference, \
    emphasis
from docutils.writers import Writer
from docutils.core import publish_string
from docutils.core import publish_cmdline

from pprint import pprint

from functools import wraps
import re

class WikiWriter(Writer):
    def translate(self):
        visitor = WikiVisitor(self.document)
        self.document.walkabout(visitor)
        self.output = visitor.astext()

class WikiVisitor(GenericNodeVisitor):

    def __init__(self, document):
        GenericNodeVisitor.__init__(self, document)
        self.list_item_prefix = None
        self.indent = self.old_indent = ''
        self.output = []
        self.preformat = False
        self.section_level = 0
        self.list_depth = 0
        self.in_table = 0
        self.skip_children = 0
        self.in_title = 0
        

    def log_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwds):
            node = args[1]
            #print >> sys.stderr, 'x'*50, 'Calling %s' % (f.__name__), '\n', node
            return f(*args, **kwds)
        return wrapper


    def astext(self):
        self.output = [i for i in self.output if i]
        return '\n%TOC%\n\n'+ ''.join(self.output) + '\n\n\n'

    @log_decorator
    def visit_Text(self, node):
        if self.skip_children: 
            return
        data = node.astext()
        if not self.preformat:
            data = data.lstrip('\n\r')
            data = data.replace('\r', '')
            data = data.replace('\n', ' ')
        if self.in_title:
            data = re.sub('[0-9\.]+', '', data)
        self.output.append(data)
    
    @log_decorator
    def default_visit(self, node):
        pass
    def default_departure(self, node):
        pass

    def visit_document(self, node):
        pass
    def depart_document(self, node):
        pass

    @log_decorator
    def visit_paragraph(self, node):
        if self.in_table or self.list_depth:
            return 
        self.output.append(self.indent)
    def depart_paragraph(self, node):
        if self.in_table or self.list_depth:
            return 
        self.output.append('\n\n')

    def visit_docinfo(self, node):
        '''ignore it'''
        self.skip_children = 1
    def depart_docinfo(self, node):
        self.skip_children = 0

    @log_decorator
    def visit_bullet_list(self, node):
        self.list_depth += 1
    def depart_bullet_list(self, node):
        self.list_depth -= 1
        self.output.append('\n')
                           
    @log_decorator
    def visit_enumerated_list(self, node):
        self.list_depth += 1
    def depart_enumerated_list(self, node):
        self.list_depth -= 1
        self.output.append('\n')


    def visit_list_item(self, node):
        self.old_indent = self.indent
        self.indent = self.list_item_prefix
        self.output.append('   * ')
    def depart_list_item(self, node):
        self.indent = self.old_indent
        self.output.append('\n')

    @log_decorator
    def visit_field_list(self, node):
        self.list_depth += 1
        self.output.append('\n')
    def depart_field_list(self, node):
        self.list_depth -= 1
        self.output.append('\n\n')

    @log_decorator
    def visit_field_name(self, node):
        self.output.append('\n   ') # 1. xxx
    def depart_field_name(self, node):
        self.output.append(': ') 

    #def visit_definition_list(self, node):
        #print 'xxxxxxx'
        #pass
    #def depart_definition_list(self, node):
        #print 'XXXXXXX'
        #pass
    #def visit_definition_list_item(self, node):
        #print 'yyyyyyy'
        #pass
    #def depart_definition_list_item(self, node):
        #print 'YYYYYYY'
        #pass
        
    def visit_literal_block(self, node):
        self.output.extend(['\n', '<verbatim>', '\n'])
        self.preformat = True
    def depart_literal_block(self, node):
        self.output.extend(['\n', '</verbatim>', '\n\n'])
        self.preformat = False
        
    def visit_reference(self, node):
        if node.has_key('refuri'):
            href = node['refuri']
        elif node.has_key('refid'):
            href = '#' + node['refid']
        else:
            href = None
        self.output.append('[[' + href + '][')
    def depart_reference(self, node):
        self.output.append(']]')

    def visit_section(self, node):
        self.section_level += 1
    def depart_section(self, node):
        self.section_level -= 1
        self.output.append('\n')

    def visit_title(self, node):
        self.in_title = 1
        tag = '\n---++' + ('+' * self.section_level) + ' '
        self.output.append(tag)
    def depart_title(self, node):
        self.in_title = 0
        self.output.append('\n\n')
        self.list_depth = 0
        self.indent = ''

    def visit_title_reference(self, node):
        self.output.append("`")
    def depart_title_reference(self, node):
        self.output.append("`")

    ############################################################
    ###### font
    ############################################################

    @log_decorator
    def visit_emphasis(self, node):
        self.output.append("*")
    def depart_emphasis(self, node):
        self.output.append("*")
        
    @log_decorator
    def visit_strong(self, node):
        self.output.append("*")
    def depart_strong(self, node):
        self.output.append("*")

    def visit_literal(self, node):
        self.output.append('*')
        
    def depart_literal(self, node):
        self.output.append('*')

   
    def visit_table(self, node):
        '''
            +------------------------+------------+----------+----------+
            | Header row, column 1   | Header 2   | Header 3 | Header 4 |
            | (header rows optional) |            |          |          |
            +========================+============+==========+==========+
            | body row 1, column 1   | column 2   | column 3 | column 4 |
            +------------------------+------------+----------+----------+
            | body row 2             | Cells may span columns.          |
            +------------------------+------------+---------------------+
            | body row 3             | Cells may  | - Table cells       |
            +------------------------+ span rows. | - contain           |
            | body row 4             |            | - body elements.    |
            +------------------------+------------+---------------------+
        '''
        self.in_table = 1
        self.output.append('\n\n')
    def depart_table(self, node):
        self.in_table = 0
        self.output.append('\n')

    def visit_thead(self, node):
        self.thead = 1
    def depart_thead(self, node):
        self.thead = 0

    def visit_tbody(self, node):
        pass
    def depart_tbody(self, node):
        pass

    def visit_row(self, node):
        self.output.append('|')
    def depart_row(self, node):
        self.output.append('\n')

    def visit_entry(self, node):
        if self.thead:
            self.output.append('*')
        else:
            self.output.append('')
        #attrs = node.attributes
        #if attrs.has_key('morecols'):
            #s = s + 'colspan=%d '%(attrs['morecols']+1)
        #if attrs.has_key('morerows'):
            #s = s + 'rowspan=%d '%(attrs['morerows']+1)
        #self.w('<%svalign="top" align="left">'%s)

    def depart_entry(self, node):
        if self.thead:
            self.output.append('*|')
        else:
            self.output.append('|')


if __name__ == '__main__':
    publish_cmdline(writer=WikiWriter())
