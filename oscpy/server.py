#!/usr/bin/env python

#
# server.py
#
# This is a simple example OSC server that creates a UDP
# socket which listens on port 8000 and prints the OSC
# messages that it receives to the shell.
#

from socket import *
from oscutil import *

sock = socket(AF_INET,SOCK_DGRAM)
port = 8000
sock.bind(('',port))

while True:
    m,addr = sock.recvfrom(4096)
    print 'got osc message from %s' % (str(addr))
    (message,m) = read_osc_message(m,True)
