import sys, string, select, threading, os.path, time
from socket import *
import xbmc
from threading import Thread  


#class XplMessage() :
#    
#    def __init__(self, type, schema):
#        self.type = type
#        self.schema = schema
#        self.source =""
#        self.target = "*"
#        self.properties = {}
    
       

class Xpl() : 
    def __init__(self, source, ip):
        self.source = source
        self.ip = ip
        self.port = 3865
        self.buff = 1500
        self.version = "1.0"
        self._stop = False
        self._socketTimeout = 4
        addr = ("0.0.0.0",self.port)
        
        
        self.udpSocket = socket(AF_INET,SOCK_DGRAM)
        # Try and bind to the base port
        try :
            self.udpSocket.bind(addr)
            print("Binding to 3865")
        except :
            # A hub is running, so bind to a high port
            self.port = 50000
            foundPort = False
            while( not foundPort ):
                xbmc.log("FA:Binding to 50000")
                addr = (self.ip, self.port)
                try :
                    self.udpSocket.bind(addr)
                    foundPort = True
                except :
                    self.port += 1
        self.heartBeat()
        xbmc.log("FA:Heartbeat sent")
        self.t = Thread(target=self.listenForPackets)
        xbmc.log("Created listen Thread")
        self.t.start()
        print( "Main thread returns")
        
        
        
    def listenForPackets(self):
        xbmc.log( "FA:Listening in for packets and stuff" )
        try: 
            while( self._stop != True) :
                readable, writeable, errored = select.select([self.udpSocket],[],[],self._socketTimeout)
                if len(readable) == 1 :
                    data,addr = self.udpSocket.recvfrom(self.buff)
                    self.parse(data)
        except(SystemExit): 
            self.stop()
            
            
    
    def parse(self, data):
        xbmc.log( data )
    
    def heartBeat(self):
        xbmc.log( "Sending heartbeat" )
        self.sendBroadcast("xpl-stat", "*","hbeat.app", "interval=1\nport=" + str(self.port) + "\nremote-ip=" + self.ip + "\nversion=" + self.version)
        self.heartbeat_timer = threading.Timer(60, self.heartBeat)
        self.heartbeat_timer.start()

    
    def sendBroadcast(self, type, target, schema, body) :
        hbSock = socket(AF_INET,SOCK_DGRAM)
        hbSock.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
        msg = "xpl-stat\n{\nhop=1\nsource=" + self.source + "\ntarget="+target+"\n}\n"+schema+"\n{\n"+ body + "\n}\n"
        hbSock.sendto(msg,("255.255.255.255",3865))
        
    def stop(self):
        xbmc.log("FA:Stopping xpl")
        self._stop = True
        self.heartbeat_timer.cancel()
        self.sendBroadcast("xpl-stat", "*","hbeat.end", "")
        time.sleep(self._socketTimeout + 1)
        self.udpSocket.close()
