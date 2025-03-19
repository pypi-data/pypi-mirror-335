import struct
import select
from .udp import UDPClient, MulticastReceiver
import socket

SERVER_PORT = 7321
MCAST_GROUP = "238.0.0.1"

Filter = lambda id, mask, extended : {"can_id":id, "can_mask":mask, "extended":extended}

class InetCAN():    
    WRITE_DATA       = 101
    SET_GROUP        = 102
    ADD_RECEIVER     = 103
    SET_FILTER       = 104
       
    def __init__(self, ip, group, iport=SERVER_PORT):
        self.__ucast_sender = UDPClient(ip, iport)
        self._mcast_receiver_dict = {} # {gport:mcast_receiver, ...}
        
        self.setGroup(group)
        
    def __del__(self):
        self.__ucast_sender.close()
        for receiver in self._mcast_receiver_dict.values():
            receiver.close()
               
    def write(self, arbitration_id, data, is_extended=False):
        self.__ucast_sender.sendTo( (self.WRITE_DATA, arbitration_id, data, is_extended) )
    
    def read(self, gport):
        if gport in self._mcast_receiver_dict.keys():
            readable, _, _ = select.select([self._mcast_receiver_dict[gport]], [], [], 10e-3)
            if readable:
                message = self._mcast_receiver_dict[gport].recvFrom()
                if message:                
                    dlc, arbitration_id = struct.unpack(">BH", message.payload[:3])
                    data = struct.unpack(f">{dlc}B", message.payload[3:])
                    return arbitration_id, data
        return None, None

    def setGroup(self, group):        
        self.__group = group
        self.__ucast_sender.sendTo( (self.SET_GROUP, group) )
    
    def setFilter(self, gport, filter):
        self.__ucast_sender.sendTo( (self.SET_FILTER, gport, filter) )
    
    def addMcastReceiver(self, gport, *args, filter=None):
        filter = filter or []
        filter.extend(Filter(id, 0x7ff, False) for id in args)
        
        mcast_receiver = MulticastReceiver(group=self.__group, port=gport)
        self._mcast_receiver_dict[gport] = mcast_receiver

        self.__ucast_sender.sendTo((self.ADD_RECEIVER, gport, filter))

    def countReceiver(self):
        return len(self._mcast_receiver_dict)
    
    def clearRecvBuffer(self, gport):
        self._mcast_receiver_dict[gport].clearRecvBuffer()

