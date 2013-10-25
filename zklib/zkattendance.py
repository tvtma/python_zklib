from struct import pack, unpack
from datetime import datetime, date

from zkconts import *

def getSizeAttendance(self):
    """Checks a returned packet to see if it returned CMD_PREPARE_DATA,
    indicating that data packets are to be sent

    Returns the amount of bytes that are going to be sent"""
    command = unpack('HHHH', self.data_recv[:8])[0] 
    if command == CMD_PREPARE_DATA:
        size = unpack('I', self.data_recv[8:12])[0]
        return size
    else:
        return False


def reverseHex(hexstr):
    tmp = ''
    for i in reversed( xrange( len(hexstr)/2 ) ):
        tmp += hexstr[i*2:(i*2)+2]
    
    return tmp
    
def zkgetattendance(self):
    """Start a connection with the time clock"""
    command = CMD_ATTLOG_RRQ
    command_string = ''
    chksum = 0
    session_id = self.session_id
    reply_id = unpack('HHHH', self.data_recv[:8])[3]

    buf = self.createHeader(command, chksum, session_id,
        reply_id, command_string)
    self.zkclient.sendto(buf, self.address)
    print buf.encode("hex")
    #try:
    self.data_recv, addr = self.zkclient.recvfrom(1024)
    self.session_id = unpack('HHHH', self.data_recv[:8])[2]
    
    if getSizeAttendance(self):
        bytes = getSizeAttendance(self)
        while bytes > 0:
            data_recv, addr = self.zkclient.recvfrom(1032)
            self.attendancedata.append(data_recv)
            bytes -= 1024
            
    data_recv = self.zkclient.recvfrom(8)
    
    attendance = []
    
    if len(self.attendancedata) > 0:
        # The first 4 bytes don't seem to be related to the user
        for x in xrange(len(self.attendancedata)):
            if x > 0:
                self.attendancedata[x] = self.attendancedata[x][8:]
        
        attendancedata = ''.join( self.attendancedata )
        
        attendancedata = attendancedata[14:]
        
        
        while (len(attendancedata) / 40) > 0:
            
            uid, state, timestamp, space = unpack( '24s1s4s11s', attendancedata.ljust(40)[:40] )
            
            
            # Clean up some messy characters from the user name
            #uid = unicode(uid.strip('\x00|\x01\x10x'), errors='ignore')
            uid = uid.split('\x00', 1)[0]
            #print "%s, %s, %s" % (uid, state, decode_time( int( reverseHex( timestamp.encode('hex') ), 16 ) ) )
            
            attendance.append( ( uid, int( state.encode('hex'), 16 ), decode_time( int( reverseHex( timestamp.encode('hex') ), 16 ) ) ) )
            
            attendancedata = attendancedata[40:]
        
    return attendance
    #except:
        #return False
    
