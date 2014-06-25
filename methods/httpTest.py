# Class to perform Web experience test

import urllib.parse
import time
import statistics
import io
import gzip

#-----------------------------------------------------------------------
# fakeUA included in the directory
import re
from methods.fakeUA import UserAgent
#import fakeUASettings
#import fakeUAUtils

ua = UserAgent()

HTML = 'HTML'
JS = 'Javascript'
CSS = 'CSS'
IMG = 'Image'

from methods.urlParser import MyHTMLParser
from methods.urlParser import MyCSSParser


class httpTests(object):
    '''
    This class takes in single URL and evaluates for pageload times and
    data values from interface
    '''

    def __init__(self, url):
        # data in Bytes and time in ms
        self.url = url      # full url
        self.IP = []
        self.domain = None
        self.times = {}  # {url:download_ms}
        self.ttfb = {}  # {url:download_ms}
        self.sizes = {}  # dataIn {url:size_Bytes}
        self.times_by_type = {}  # {asset_type:download_seconds}
        self.html = {}  # {url:html}
        self.link_types = {}  # {type:set([url])}
        self.header_size = {}  # dataOut
        self.response = {}
        self.dataIn_by_type = {}
        self.dataOut_by_type = {}
        self.errorStatus = ''
        #self.dataRate = {}  # {url:datarate kbps}
        self.dataRate = []  # {url:datarate kbps}
        self.throughPut = 0

    @property
    def total_download_seconds(self):
        return sum(self.times.values())

    @property
    def total_data_out(self):
        return sum(self.header_size.values())

    @property
    def total_data_in(self):
        return sum(self.sizes.values())

    def measure(self, url, asset_type):
        '''
        measure time and data values for one url
        '''
        if url.startswith('//'):
            url = 'http:' + url
        elif url.startswith('/'):
            url = 'http://' + self.domain + url
        elif not url.startswith('/') and not url.startswith('http'):
            url = 'http://' + self.domain + '/' + url

        if url not in self.html:
            # Randomize user-agent and ignore robots.txt to ensure server
            # isn't gaming load times.
            try:
                opener = urllib.request.build_opener()
                req = urllib.request.Request(url,
                headers={'User-Agent': ua.random})
                t0 = time.perf_counter()
                resp = opener.open(req)
                htmlFB = resp.read(1)
                #html = urllib.request.urlopen(req).read()
                t1 = time.perf_counter() - t0
                htmlremaining = resp.read()
                td = time.perf_counter() - t0
                html = htmlFB + htmlremaining
                htmlOpen = urllib.request.urlopen(req)
                self.response[url] = str(htmlOpen.status) + " " \
                + htmlOpen.reason
            except:
                t1 = 0
                td = 0
                html = b''
            hdrString = 0
            for txt in req.header_items():
                hdrString += len(": ".join(list(txt)))
            self.header_size[url] = hdrString
            self.sizes[url] = len(html)
            self.ttfb[url] = t1 * 1000
            self.times[url] = td * 1000
            self.times_by_type.setdefault(asset_type, 0)
            self.times_by_type[asset_type] += td * 1000
            self.dataIn_by_type.setdefault(asset_type, 0)
            self.dataIn_by_type[asset_type] += len(html)
            self.dataOut_by_type.setdefault(asset_type, 0)
            self.dataOut_by_type[asset_type] += hdrString
            self.html[url] = html
        return self.html[url]

    def httpPageRequest(self):
        # make initial html request for the given url
        # and parse for following GET requests
        getReq = MyHTMLParser()
        self.domain = urllib.parse.urlparse(self.url).netloc
        i = 1
        total = i
        reqOut = (('\rMeasuring %i of %i %.02f%%: %s'
                % (i, total, i / float(total) * 100, self.url[:30])).ljust(40))
        try:
            html = self.measure(url=self.url, asset_type=HTML)
            if html[0:2] == b'\x1f\x8b':  # gzip compressed
                htmlstream = io.BytesIO(html)
                gzipper = gzip.GzipFile(fileobj=htmlstream, mode="rb")
                html = gzipper.read()
            try:
                htmlResp = html.decode('utf-8')
            except UnicodeDecodeError:
                htmlResp = html.decode('Latin-1')
            getReq.feed(htmlResp)
            self.errorStatus = ''
        except:
            self.errorStatus = 'URL Error'
        reqOut += '\n' + self.errorStatus + \
        '\nMeasuring GET Requests for the given URL'
        return reqOut

    def GetRequest(self, getType=None):
        # js, css, image GET Requests measurements
        getReq = MyHTMLParser()
        reqOut = ('\tMeasured %i GET requests.' %
         (len(getReq.reqType[getType])))

        while getReq.reqType[getType]:
            reqUrl = getReq.reqType[getType].pop()
            respReq = self.measure(url=reqUrl, asset_type=getType)
            if getType is 'CSS':
                cssParser = MyCSSParser(cssFile=respReq)
                getReq.reqType['Image'].extend(cssParser.parseCss(
                homeFolder=reqUrl[:reqUrl.rfind('/') + 1]))
                #TODO unique image get requests
        return reqOut

    def httpOutput(self):
        outputTxt = ''
        if len(self.times) >= 1:
            outputTxt += '\n' + '-' * 80 + \
            '\nDownload times and Data Transactions by asset type:'
            fmt = '%%%d.02f  %%%d.02f %%%d.02f %%6.02f%%%% %%s' \
            % (len('%.02f' % max(self.times_by_type.values())),
            len('%.02f' % max(self.header_size.values())),
            len('%.02f' % max(self.sizes.values())))
            for asset_type, download_time in sorted(list(
                self.times_by_type.items()), key=lambda o: o[1]):
                outputTxt += '\n' + fmt \
                % ((download_time / 1000), self.dataOut_by_type[asset_type],
                self.dataIn_by_type[asset_type],
                (download_time / self.total_download_seconds * 100), asset_type)
            #self.throughPut = (sum(self.header_size.values()) +
                #sum(self.sizes.values())) /
                #(round(sum(self.times.values()) / 1000))
            for url, download_time in sorted(list(self.times.items()),
            key=lambda o: o[1]):
                if download_time is not 0:
                    self.dataRate.append((self.sizes[url] +
                    self.header_size[url]) / ((download_time / 1000)))
            self.throughPut = statistics.mean(self.dataRate)
            outputTxt += '\n' + '-' * 80 + '\nAverage Throughput is %.3f KBps' \
            % (self.throughPut / 1024)
        else:
            outputTxt += 'Error: %s' % self.errorStatus
        return outputTxt
