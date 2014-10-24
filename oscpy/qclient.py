#!/usr/bin/env python

#
# qclient.py
#
# A simple OSC client that sends OSC messages on port 8000
# in response to UI events
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *
import sys
import struct
import time

from oscutil import *

class OSCController(QWidget):
    '''A simple widget that creates some basic controls that send OSC events'''

    def __init__(self):
        super(OSCController,self).__init__()
        self.oscsocket = QUdpSocket()
        self.oschost = QHostAddress(QHostAddress.LocalHost)
        self.oscport = 8000

        self.toplayout = QVBoxLayout(self)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1000)
        self.slider.setTracking(True)
        self.slider.valueChanged.connect(self.sliderCB)
        self.toplayout.addWidget(self.slider)

        self.trigger = QPushButton('Impulse')
        self.trigger.clicked.connect(self.triggerCB)
        self.toplayout.addWidget(self.trigger)

        self.bundle = QPushButton('Bundle')
        self.bundle.clicked.connect(self.bundleCB)
        self.toplayout.addWidget(self.bundleCB)

        self.gridlayout = QGridLayout()
        # we need an intermediate function to capture the values of i,j
        def toggleCBFor(i,j):
            return lambda val: self.toggleCB(val,i,j)

        for i in range(8):
            for j in range(8):
                toggle = QCheckBox()
                toggle.clicked.connect(toggleCBFor(i,j))
                self.gridlayout.addWidget(toggle,i,j)
        self.toplayout.addLayout(self.gridlayout)


    def sliderCB(self,value):
        self.sendOSC(osc_message('/slider',[float(value)/1000.0]))

    def triggerCB(self):
        self.sendOSC(osc_message('/trigger',[Impulse()]))

    def bundleCB(self):
        self.sendOSC(osc_bundle(Timetag(time.time()),
                                [osc_bundle(Timetag(time.time()),
                                            [osc_message('/trigger',[Impulse()]),
                                             osc_bundle(Timetag(time.time()),[])])]))

    def toggleCB(self,state,i,j):
        self.sendOSC(osc_message('/toggle%d%d'%(i,j),[bool(state)]))

    def sendOSC(self,m):
        self.oscsocket.writeDatagram(QByteArray(m),self.oschost,self.oscport)

app = QApplication(sys.argv)
osc = OSCController()
osc.show()

# the following line makes the window appear on top
# of the other windows on OSX
osc.raise_()

sys.exit(app.exec_())
