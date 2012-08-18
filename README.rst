commands 
===============


rst2wiki: 
    从http://code.google.com/p/rst2trac/source/browse/trunk/rst2wiki.py?r=4 下载.

rst2twiki: 
    a tool convert docs from rst to twiki

install
=================

    pip install git+git://github.com/idning/rst2twiki.git


类似工具: 
==================
    
    wikir: http://code.google.com/p/wikir/  
    rst2wiki: http://code.google.com/p/rst2trac/source/browse/trunk/rst2wiki.py?r=4 

    both has no support on table, so I do it

    pandoc : rst => wiki
    pandoc -s -S -w mediawiki --toc test.rst -o test.pandoc.wiki

    pandoc 对table 是直接转成 html, 不太好，但是其它方面都无懈可击.


