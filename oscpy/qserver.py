#!/usr/bin/env python

#
# qserver.py
#
# A simple OSC server that listens on port 8000 for OSC
# messages and displays them in a PyQt window.
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *
import sys
import struct
import time

from oscutil import *

class OSCWidget(QWidget):
    '''A simple widget that starts an OSC server and displays received messages in a scroll view'''

    def __init__(self):
        super(OSCWidget,self).__init__()
        self.oscsocket = QUdpSocket()
        port = 8000
        self.oscsocket.bind(port)
        self.oscsocket.readyRead.connect(self.dataCB)
        self.osclabels = {}

        self.vwidget = QWidget()
        # add a layout to contain the layout with the osc data followed
        # by a spacer to take up the remaining space
        self.vlayout = QVBoxLayout(self.vwidget) 
        self.gridlayout = QGridLayout()
        self.vlayout.addLayout(self.gridlayout)
        self.vlayout.addSpacerItem(QSpacerItem(0,0,QSizePolicy.Minimum,QSizePolicy.Expanding))

        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        if True:
            self.scroll.setWidget(self.vwidget)
            self.scroll.setWidgetResizable(True)
        else:
            self.vwidget.show()
            self.vwidget.raise_()

        self.toplayout = QVBoxLayout(self)
        self.toplayout.setContentsMargins(5,5,5,5)
        self.toplayout.addWidget(QLabel("OSC Message Data:"))
        self.toplayout.addWidget(self.scroll)

    def dataCB(self):
        'Callback for when new data is received on the socket'

        while self.oscsocket.hasPendingDatagrams():
            m,host,port = self.oscsocket.readDatagram(self.oscsocket.pendingDatagramSize())
            while len(m):
                (address,data,m) = read_osc_message(m)
                l = self.osclabels.get(address)
                if l is None:
                    row = self.gridlayout.rowCount()
                    l = QLabel()
                    self.gridlayout.addWidget(QLabel(address),row,0)
                    self.gridlayout.addWidget(l,row,1)
                    self.osclabels[address] = l
                l.setText(str(data))
        
app = QApplication(sys.argv)
osc = OSCWidget()
osc.resize(400,600)
osc.show()

# the following line makes the window appear on top
# of the other windows on OSX
osc.raise_()

sys.exit(app.exec_())
