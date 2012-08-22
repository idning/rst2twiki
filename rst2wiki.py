#!/usr/bin/env python
#copy from : http://code.google.com/p/rst2trac/source/browse/trunk/rst2wiki.py?r=4

import sys
from docutils.nodes import SparseNodeVisitor, GenericNodeVisitor, paragraph, title_reference, \
    emphasis
from docutils.writers import Writer
from docutils.core import publish_string
from docutils.core import publish_cmdline
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
        self.list_depth = 0
        self.list_item_prefix = None
        self.indent = self.old_indent = ''
        self.output = []
        self.preformat = False
        self.section_level = 0
        self.list_depth = 0
        self.in_table = 0
        self.skip_children = 0
        self.current_row  = 0
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
        return '\n>>>\n\n'+ ''.join(self.output) + '\n\n<<<\n'

    @log_decorator
    def visit_Text(self, node):
        #print "Text", node
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


    ############################################################
    ###### list 
    ############################################################
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

    @log_decorator
    def visit_list_item(self, node):
        self.old_indent = self.indent
        self.indent = self.list_item_prefix
        self.output.append('* ')

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
        pass
    def depart_field_name(self, node):
        self.output.append(': \n') 

    def visit_literal_block(self, node):
        self.output.extend(['<pre><nowiki>', '\n'])
        self.preformat = True

    def depart_literal_block(self, node):
        self.output.extend(['\n', '</nowiki></pre>', '\n\n'])
        self.preformat = False
        

    def visit_paragraph(self, node):
        if self.in_table or self.list_depth:
            return 
        self.output.append(self.indent)
        
    def depart_paragraph(self, node):
        if self.in_table or self.list_depth:
            return 
        self.output.append('\n\n')
        if self.indent == self.list_item_prefix:
            # we're in a sub paragraph of a list item
            self.indent = ' ' * self.list_depth
        
    def visit_reference(self, node):
        if node.has_key('refuri'):
            href = node['refuri']
        elif node.has_key('refid'):
            href = '#' + node['refid']
        else:
            href = None
        self.output.append('[' + href + ' ')

    def depart_reference(self, node):
        self.output.append(']')

    def visit_section(self, node):
        self.section_level += 1
    def depart_section(self, node):
        self.section_level -= 1
        self.output.append('\n')

    @log_decorator
    def visit_title(self, node):
        self.in_title = 1
        self.output.append('\n==%s ' % ('='*self.section_level))

    def depart_title(self, node):
        self.in_title = 0
        self.output.append(' ==%s\n\n' % ('='*self.section_level))        

    def visit_title_reference(self, node):
        self.output.append("`")

    def depart_title_reference(self, node):
        self.output.append("`")

    ############################################################
    ###### font
    ############################################################

    @log_decorator
    def visit_emphasis(self, node):
        self.output.append("''")
    def depart_emphasis(self, node):
        self.output.append("''")
        
    @log_decorator
    def visit_strong(self, node):
        self.output.append("'''")
    def depart_strong(self, node):
        self.output.append("'''")

    def visit_literal(self, node):
        self.output.append('<pre>')
        
    def depart_literal(self, node):
        self.output.append('</pre>')
   

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
        self.output.append('{| cellpadding="5" class="mainVisual" \n')
    def depart_table(self, node):
        self.in_table = 0
        self.output.append('|}\n\n')

    def visit_thead(self, node):
        #self.output.append('|-\n')
        self.thead = 1
    def depart_thead(self, node):
        self.thead = 0

    def visit_tbody(self, node):
        self.current_row = 0
        pass
    def depart_tbody(self, node):
        pass

    def visit_row(self, node):
        if self.thead:
            self.output.append('|- \n')
        else:
            self.current_row = (self.current_row +1) %2  # even/odd
            x = self.current_row + 1
            self.output.append('|- class="lineVisual%d"\n' % x)
    def depart_row(self, node):
        pass
        #self.output.append('\n')

    def visit_entry(self, node):
        if self.thead:
            self.output.append('!')
        else:
            self.output.append('|')
        #attrs = node.attributes
        #if attrs.has_key('morecols'):
            #s = s + 'colspan=%d '%(attrs['morecols']+1)
        #if attrs.has_key('morerows'):
            #s = s + 'rowspan=%d '%(attrs['morerows']+1)
        #self.w('<%svalign="top" align="left">'%s)

    def depart_entry(self, node):
        self.output.append('\n')
        
if __name__ == '__main__':
    publish_cmdline(writer=WikiWriter())
