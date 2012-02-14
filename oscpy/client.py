#!/usr/bin/env python

from socket import *
import struct
import time

from oscutil import *

sock = socket(AF_INET,SOCK_DGRAM)

# send individual datagrams for each of the OSC types
sock.sendto(osc_message('/testint',[1]),("localhost",8000))
sock.sendto(osc_message('/testfloat',[1.0,2.0,3.0]),("localhost",8000))
sock.sendto(osc_message('/teststring',["hello"]),("localhost",8000))
sock.sendto(osc_message('/testblob',[Blob("blob")]),("localhost",8000))
sock.sendto(osc_message('/testtrue',[True]),("localhost",8000))
sock.sendto(osc_message('/testfalse',[False]),("localhost",8000))
sock.sendto(osc_message('/testnull',[None]),("localhost",8000))
sock.sendto(osc_message('/testimpulse',[Impulse()]),("localhost",8000))
sock.sendto(osc_message('/testtimetag',[Timetag(time.time())]),("localhost",8000))

# send a single datagram with all of the OSC types
sock.sendto(
    osc_message('/testint',[2]) + 
    osc_message('/testfloat',[2.0,3.0,4.0]) + 
    osc_message('/teststring',["hello2"]) + 
    osc_message('/testblob',[Blob("blob2")]) + 
    osc_message('/testtrue',[True]) + 
    osc_message('/testfalse',[False]) + 
    osc_message('/testnull',[None]) + 
    osc_message('/testimpulse',[Impulse()]) +
    osc_message('/testtimetag',[Timetag(time.time())]),
    ("localhost",8000))

