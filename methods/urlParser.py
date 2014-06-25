from html.parser import HTMLParser
from methods import tinycss2


class MyHTMLParser(HTMLParser):
    # parse html response and return GET Requests
    # input argument is the HTML response
    # output is dict of parsed GET Requests URLs
    reqType = {'Javascript': [], 'CSS': [], 'Image': []}

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if attr[0] in ('href', 'src'):
                if '.css' in attr[1]:
                    self.reqType['CSS'].append(attr[1])
                elif '.js' in attr[1]:
                    self.reqType['Javascript'].append(attr[1])
                elif 'a' not in tag:
                    self.reqType['Image'].append(attr[1])


class MyCSSParser(object):
    #parse css file and get urls
    # input argument is the CSS response
    # output is list of parsed GET Requests URLs
    def __init__(self, cssFile):
        self.resp = cssFile
        self.parsedUrls = []

    def parseCss(self, homeFolder=''):
        #parse css response and return list of urls
        rul, encod = tinycss2.parse_stylesheet_bytes(css_bytes=self.resp)
        for rule in rul:
            try:
                for token in rule.content:
                    if tinycss2.ast.URLToken == type(token) and \
                    token.value != 'none':
                        if token.value.startswith('../'):
                            self.parsedUrls.append(homeFolder + token.value)
                        else:
                            self.parsedUrls.append(token.value)
            except (AttributeError, TypeError):
                pass
        urls = set(self.parsedUrls)
        return urls
