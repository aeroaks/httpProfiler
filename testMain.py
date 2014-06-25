# -*- coding: utf-8 -*-
# Import GUI and implement threaded processing of tasks
# Author: Akshay Verma

import sys
import socket
from datetime import datetime
from threading import Timer
from os import makedirs
import urllib.request, os.path, csv

from methods import httpTest


class MainDialog(object):
    # main dialog that opens when program starts
    def __init__(self):
        self.testDate = datetime.now().strftime("%Y%m%d")
        self.csvFileSetup()
        self.schedTime = datetime.now()
        self.netDetails = {}
        self.schTestInfo = {}

        self.webTestInput

        self.schedThread = schedThread()
        self.schedThread.testStartSignal.connect(self.startSchedTest)

    def inputSched(self):
        '''
        input scheduler date time
        '''
        if self.schedDialog is None:
            self.schedDialog = SchedDialog()
        self.schedDialog.exec_()

        self.outputDisplay.append('\nInput Date Time for Scheduler')
        if self.schedDialog.dateTime:
            # set scheduler date time value
            self.schedTime = datetime.now().replace(
                year=self.schedDialog.dateTime['yr'],
                month=self.schedDialog.dateTime['mn'],
                day=self.schedDialog.dateTime['dy'],
                hour=self.schedDialog.dateTime['hr'],
                minute=self.schedDialog.dateTime['mi'],
                second=0, microsecond=0)
            self.outputDisplay.append('''\nTest schedule set for
            %02d/%02d/%02d %02d:%02d\n''' %
            (self.schedTime.day, self.schedTime.month,
            self.schedTime.year, self.schedTime.hour,
            self.schedTime.minute))
            self.schedThread.dateTime = self.schedTime
            self.schedThread.start()
        else:
            # no value selected
            self.outputDisplay.append('\nNo Date Time Selected\n')
        self.schedDialog = None

    def startSchedTest(self):
        self.outputDisplay.append('\nTest Schedule Started\n')

        if 'testweb' in self.schTestInfo:
            # perform web exp tests
            dt = datetime.now()
            dt = dt.isoformat().split('T')
            dt[1] = dt[1].split('.')[0]
            testDate = dt[0] + ' ' + dt[1]
            self.webTestMethod(httpurls=self.schTestInfo['webAddr'],
            httpreps=self.schTestInfo['webRep'], Date=testDate)

    def csvFileSetup(self):
        #generate files with header
        if not os.path.exists('csv'):
            makedirs('csv')

        setnet = 'csv/setNetworks' + self.testDate + '.csv'
        if not os.path.isfile(setnet):
            setNet = open(setnet, 'w', newline='')
            setNetWriter = csv.writer(setNet, quoting=csv.QUOTE_NONNUMERIC)
            setNetWriter.writerow(['id','name','local','busy','status','locationId','mobile'])
            setNet.close()

        setup = 'csv/setup' + self.testDate + '.csv'
        if not os.path.isfile(setup):
            setup = open(setup, 'w', newline='')
            setupWriter = csv.writer(setup, quoting=csv.QUOTE_NONNUMERIC)
            setupWriter.writerow(['id','sourceNetworkId','destNetworkId','dateTime','voiceData','clientId'])
            setup.close()

        seturl = 'csv/setUrls' + self.testDate + '.csv'
        if not os.path.isfile(seturl):
            setUrl = open(seturl, 'w', newline='')
            setUrlWriter = csv.writer(setUrl, quoting=csv.QUOTE_NONNUMERIC)
            setUrlWriter.writerow(['id', 'url', 'IP'])
            setUrl.close()

        measur = 'csv/measurement' + self.testDate + '.csv'
        if not os.path.isfile(measur):
            measure = open(measur, 'w', newline='')
            measureWriter = csv.writer(measure, quoting=csv.QUOTE_NONNUMERIC)
            measureWriter.writerow(['id', 'setupId', 'parameterId', 'bytes', 'timeTaken', 'urlId', 'sent'])
            measure.close()

        measurDet = 'csv/measurementDetail' + self.testDate + '.csv'
        if not os.path.isfile(measurDet):
            measDet = open(measurDet, 'w', newline='')
            measDetWriter = csv.writer(measDet, quoting=csv.QUOTE_NONNUMERIC)
            measDetWriter.writerow(['id', 'measurementId' , 'url', 'bytes', 'timeTaken', 'ttfb'])
            measDet.close()

    def outputToCSV(self, nw={}, test=0, date=None, httpObj=None,
        pathObj=None, nwObj=None, ftpObj=None, vidObj=None):
        '''
        output to CSV
        '''
        #read CSV and set id according to latest value
        setup = 'csv/setup' + self.testDate + '.csv'
        for row in csv.reader(open(setup, 'r')):
            if row[0] == 'id':
                setupId = 1
            else:
                setupId = int(row[0]) + 1

        seturl = 'csv/setUrls' + self.testDate + '.csv'
        for row in csv.reader(open(seturl, 'r')):
            if row[0] == 'id':
                setUrlId = 1
            else:
                setUrlId = int(row[0]) + 1

        measur = 'csv/measurement' + self.testDate + '.csv'
        for row in csv.reader(open(measur, 'r')):
            if row[0] == 'id':
                measureId = 1
            else:
                measureId = int(row[0]) + 1

        measurDet = 'csv/measurementDetail' + self.testDate + '.csv'
        for row in csv.reader(open(measurDet, 'r')):
            if row[0] == 'id':
                measDetId = 1
            else:
                measDetId = int(row[0]) + 1

        # to save only unique network config
        uniqueNetwork = 1
        setnet = 'csv/setNetworks' + self.testDate + '.csv'
        for row in csv.reader(open(setnet, 'r')):
            if (row[1] == nw['name'] and row[2] == nw['local'] and
            row[4] == nw['status'] and row[5] == nw['locn'] and
            row[6] == nw['device']):
                setNetId = int(row[0])
                uniqueNetwork = 0
            elif row[0] == 'id':
                setNetId = 1
                uniqueNetwork = 1
            else:
                setNetId = int(row[0]) + 1

        setNet = open(setnet, 'a', newline='')
        setNetWriter = csv.writer(setNet, quoting=csv.QUOTE_NONNUMERIC)
        setup = open(setup, 'a', newline='')
        setupWriter = csv.writer(setup, quoting=csv.QUOTE_NONNUMERIC)
        setUrl = open(seturl, 'a', newline='')
        setUrlWriter = csv.writer(setUrl, quoting=csv.QUOTE_NONNUMERIC)
        measure = open(measur, 'a', newline='')
        measureWriter = csv.writer(measure, quoting=csv.QUOTE_NONNUMERIC)
        measDet = open(measurDet, 'a', newline='')
        measDetWriter = csv.writer(measDet, quoting=csv.QUOTE_NONNUMERIC)

        if uniqueNetwork == 1:
            setNetWriter.writerow([setNetId, nw['name'], nw['local'],
                date, nw['status'], nw['locn'], nw['device']])

        setupWriter.writerow([setupId, setNetId, '', date, 0, nw['client']])

        if test == 1:  # http tests to file
            setUrlWriter.writerow([setUrlId, httpObj.url, ''])

            measureWriter.writerow([measureId, setupId, 'Web_Resoln_Time',
                0, round((httpObj.IP[1]) * 1000), httpObj.url, 0])
            measureId += 1
            for types, typeTimes in sorted(list(httpObj.times_by_type.items()),
                key=lambda o: o[0]):
                measureWriter.writerow([measureId, setupId, 'Web_' + types,
                httpObj.dataOut_by_type[types],
                round((httpObj.times_by_type[types]) * 1000), httpObj.url, 0])
                measureWriter.writerow([measureId + 1, setupId, 'Web_' + types,
                httpObj.dataIn_by_type[types],
                round((httpObj.times_by_type[types]) * 1000), httpObj.url, 1])

                for url, download_time in sorted(list(httpObj.times.items()),
                    key=lambda o: o[1]):
                    if '.js' in url:
                        paraType = 'Javascript'
                    elif '.css' in url:
                        paraType = 'CSS'
                    elif url == httpObj.url:
                        paraType = 'HTML'
                    else:
                        paraType = 'Image'

                    if paraType == types:
                        measDetWriter.writerow([measDetId, measureId, url,
                        httpObj.header_size[url], round(httpObj.times[url])])
                        measDetWriter.writerow([measDetId + 1, measureId + 1,
                        url, httpObj.sizes[url], round(httpObj.times[url]),
                        round(httpObj.ttfb[url])])
                        measDetId += 2
                measureId += 2

        setNet.close()
        setup.close()
        measure.close()
        measDet.close()

    def webTestInput(self):
        '''
        input url and repitition details for web exp test
        '''
        if self.checkNetInfo():
            if self.addrDialog is None:
                self.addrDialog = AddrDialog()
            self.addrDialog.exec_()

            if 'addr' in self.addrDialog.addrInfo:
                testDate = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                addr = self.addrDialog.addrInfo['addr']
                reps = self.addrDialog.addrInfo['rep']
                if 'schedule' in self.addrDialog.addrInfo:  # setup scheduler
                    self.schTestInfo['testweb'] = True
                    self.schTestInfo['webAddr'] = addr
                    self.schTestInfo['webRep'] = reps
                    self.outputDisplay.\
                    append('\nTest Information added to Scheduler. ')
                else:  # run test
                    self.webTestMethod(httpurls=addr, httpreps=reps,
                    Date=testDate)
            else:
                self.outputDisplay.append('\nInput address to start test.')
            self.addrDialog = None

    def webTestMethod(self, httpurls, httpreps, Date):
        '''
        Actual testing of http urls
        '''
        self.outputDisplay.append('\nStarting Web Experience Test')
        JS = 'Javascript'
        CSS = 'CSS'
        IMG = 'Image'
        asset_type = (JS, CSS, IMG)
        if len(httpurls) == 0:
            self.outputDisplay.append('Error: No URL entered!')
        else:
            urlArray = httpurls.split(',')
            for repNo in range(httpreps):
                self.outputDisplay.append("\nTest Repitition Number: "
                + str(repNo + 1))
                for testUrl in urlArray:
                    http = testUrl.find('http://')
                    https = testUrl.find('https://')
                    if http == -1 and https == -1:
                        httpUrlFull = 'http://' + testUrl.strip()
                    elif http == 0:
                        httpUrlFull = testUrl.strip()
                    elif https == 0:
                        httpUrlFull = testUrl.strip()
                    self.outputDisplay.append('Testing Link: %s' % httpUrlFull)
                    QApplication.processEvents()  # update display
                    webHttp = httpTest.httpTests(url=httpUrlFull)
                    self.outputDisplay.append(webHttp.httpPageRequest())
                    # DNS Look-up
                    try:
                        socket.inet_aton(path)
                        webPath = pathTest.pathTests(ip=testUrl.strip())
                        webPath.getHost()
                    except:
                        webPath = pathTest.pathTests(url=testUrl.strip())
                        webPath.getIP()
                    self.outputDisplay.append('\nCapturing Route details ...\n')
                    self.outputDisplay.append(webPath.dnsOutput())
                    webHttp.IP = webPath.IP
                    QApplication.processEvents()  # update display
                    for type in sorted(asset_type):
                        self.outputDisplay.append(
                            '\rMeasuring %s GET requests ...' % (type))
                        QApplication.processEvents()  # update display
                        self.outputDisplay.append(webHttp.GetRequest
                            (getType=type))
                    self.outputDisplay.append(webHttp.httpOutput())
                    # save to csv
                    self.outputToCSV(nw=self.netDetails, test=1, date=Date,
                    httpObj=webHttp)
                    self.outputDisplay.append('\nSaved to File!')


class schedThread(QThread):
    '''
    Thread where scheduler runs and emits signal on entered time.
    '''
    testStartSignal = pyqtSignal()

    def __init__(self, parent=None):
        super(schedThread, self).__init__(parent)
        self.dateTime = datetime.now()

    def run(self):
        '''
        default thread method
        '''
        delta_t = self.dateTime - datetime.today()
        secs = delta_t.seconds + 1
        t = Timer(secs, self.testStartSignal.emit)
        t.start()
        #time.sleep(6) intital testing
        #self.testStartSignal.emit()


if __name__ == "__main__":
    form = MainDialog()
    form.show()
    app.exec_()