'''
Utility functions and types for dealing with osc data
'''

import struct, time

class Message(object):
    '''This represents an OSC message'''

    def __init__(self,address,data):
        'Create an OSC message'
        self.address = address
        self.data = data

    def __repr__(self):
        return "Message('%s' : %s)" % (self.address, self.data)

class Bundle(object):
    '''This represents an OSC bundle'''

    def __init__(self,timetag,contents):
        'Create an OSC bundle'
        self.timetag = timetag
        self.contents = contents

    def __repr__(self):
        return "Bundle(%s, %s)" % (self.timetag, self.contents)

class Blob(object):
    '''This represents an OSC blob (arbritrary binary data)'''

    def __init__(self,b):
        'Create an OSC blob for the given buffer'
        self.blob = b

    def __repr__(self):
        return "Blob('%s')" % (self.blob)

class Impulse(object):
    '''This represents an OSC impulse/event'''

    def __init__(self):
        'Create an OSC impulse/event'
        pass

    def __repr__(self):
        return "Impulse()"

class Timetag(object):
    '''This represents an OSC timetag
       The .time attribute is a float time in seconds since the epoch'''

    def __init__(self,t):
        'Create an OSC timetag with the given float time value'
        self.time = t

    def __repr__(self):
        tg = time.localtime(self.time)
        return "Timetag('%s + %.08f')" % (time.asctime(tg),self.time-time.mktime(tg))


def read_string(m):
    'Read an OSC encoded string from a recieved message'
    index = m.find('\0')
    assert(index >= 0)
    s = m[:index]
    remaining_start = index + 1
    while (remaining_start % 4) != 0:
        assert(m[remaining_start] == '\0')
        remaining_start += 1
    return (s,m[remaining_start:])

def read_int(m):
    'Read an OSC encoded int from a recieved message'
    return (struct.unpack('!i',m[:4])[0],m[4:])

def read_float(m):
    'Read an OSC encoded float from a recieved message'
    return (struct.unpack('!f',m[:4])[0],m[4:])

def read_blob(m):
    'Read an OSC encoded blob from a recieved message'
    len = struct.unpack('!i',m[:4])[0]
    return (Blob(m[4:4+len]),m[4+len:])

def read_timetag(m):
    'Read an OSC encoded timetag from a recieved message'
    return (Timetag(float(struct.unpack('!q',m[:8])[0]/2.0**32)),m[8:])

def read_osc_message(m,verbose=False,indent='  '):
    'Read an OSC encoded message, returning a tuple of a Message or Bundle and a buffer containing any remaining data '

    (s,m) = read_string(m)
    if s == '#bundle':
        if len(m) < 8:
            raise RuntimeError('bundle missing timetag, ignoring')
        (timetag,m) = read_timetag(m)
        if verbose: print indent + 'bundle: %s' % (timetag)
        contents = []
        while len(m) != 0:
            (size,remainder) = read_int(m)
            bundle_element_m = remainder[:size]
            m = remainder[size:]
            (message,bundle_element_m) = read_osc_message(bundle_element_m,verbose,indent+'  ')
            contents.append(message)
        return (Bundle(timetag,contents),m)
    elif s.startswith('/'):
        address = s

        if len(m) == 0 or m[0] != ',':
            raise RuntimeError('message missing type tag string, ignoring')
        if verbose: print indent + 'message: %s' % (address)

        (typetags,m) = read_string(m)
        typetags = typetags[1:]
        if verbose: print indent + '  typetags: %s' % (typetags)

        data = []
        for t in typetags:
            if t == 'i':
                (i,m) = read_int(m)
                data.append(i)
            elif t == 'f':
                (f,m) = read_float(m)
                data.append(f)
            elif t == 's':
                (s,m) = read_string(m)
                data.append(s)
            elif t == 'b':
                (b,m) = read_blob(m)
                data.append(b)
            elif t == 'T':
                data.append(True)
            elif t == 'F':
                data.append(False)
            elif t == 'N':
                data.append(None)
            elif t == 'I':
                data.append(Impulse())
            elif t == 't':
                (tm,m) = read_timetag(m)
                data.append(tm)
            else:
                raise RuntimeError('unknown type tag "%s", ignoring remaining message elements' % (t))
        if verbose: print indent + '  data: %s' % (data)
        return (Message(address,data),m)
    else:
        raise RuntimeError('unrecognized OSC message contents')

    
def osc_int(i):
    'Convert an int to an OSC encoded int'
    return struct.pack('!i',i)

def osc_float(f):
    'Convert a float to an OSC encoded float'
    return struct.pack('!f',f)

def osc_string(s):
    'Convert a string to an OSC encoded string'
    buf = s + '\0'
    while (len(buf) % 4) != 0:
        buf += '\0'
    return buf

def osc_blob(b):
    'Convert a buffer to an OSC encoded blob'
    return struct.pack("!i",len(b)) + b

def osc_timetag(t):
    'Convert a float time to an OSC encoded timetag'
    return struct.pack('!q',int(t*(2**32)))

def osc_message(address,data):
    'Encode an OSC message given the specified OSC address and data'

    payload = ''
    tags = ','
    for d in data:
        if type(d) == int:
            tags += 'i'
            payload += osc_int(d)
        elif type(d) == float:
            tags += 'f'
            payload += osc_float(d)
        elif type(d) == str:
            tags += 's'
            payload += osc_string(d)
        elif type(d) == Blob:
            tags += 'b'
            payload += osc_blob(d.blob)
        elif type(d) == bool:
            if d:
                tags += 'T'
            else:
                tags += 'F'
        elif d is None:
            tags += 'N'
        elif type(d) == Impulse:
            tags += 'I'
        elif type(d) == Timetag:
            tags += 't'
            payload += osc_timetag(d.time)
        else:
            raise RuntimeError("Unknown type: %s" % (d.__class__))

    return osc_string(address) + osc_string(tags) + payload

def osc_bundle(timetag,contents):
    'Encode an OSC bundle given the specified OSC timetage and contents'

    data = osc_string('#bundle')
    data += osc_timetag(timetag.time)
    for c in contents:
        data += osc_int(len(c))
        data += c
    return data
