httpProfiler
============

Time measurement of webPage requests.

Requirements:
Python 3.4

Description:
Http requests are made using urllib.request module. HTML is parsed, using html.parser module, to get embedded JS, CSS and Image URLs. Image links embedded in CSS files are parsed using tinycss2 library.
