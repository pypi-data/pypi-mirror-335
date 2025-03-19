import platform
import time
import select
import socket
import struct
import signal
import threading
import pickle
from dataclasses import dataclass
import ifaddr

@dataclass
class Message:
    payload = None
    remote = None


class UDP(socket.socket):
    DEFAULT_INTERFACE = ''
    DEFAULT_SERVER_IP = '127.0.0.1'
    DEFAULT_PORT = 7321
    
    MIN_PAYLOAD_SIZE = 576
    MAX_PAYLOAD_SIZE = 65_507

    DEFAULT_GROUP = '239.8.7.6'
    DEFAULT_TTL = 2
    
    STX         = b'\xFF\xFF\xFF\xFF\x02'
    STX_ACK     = b'\xFF\xFF\xFF\xFF\x01'
    ETX         = b'\xFF\xFF\xFF\xFF\x03'
    ETX_ACK     = b'\xFF\xFF\xFF\xFF\x04'
    
    WAIT_EVENT_DELAY = 1/10
    
    def __init__(self):
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.setblocking(False)
        
        self.__local = ()
        self.__remote_set = set()
        self.__group_set = set()
        
        self.__cb_enter = lambda self, *args: self
        self.__cb_enter_args = ()
        self.__cb_leave = lambda self, *args: self
        self.__cb_leave_args = ()
        self.__cb_recv = lambda self, *args: self
        self.__cb_recv_args = ()
        self.__recv_thread = None
        self.__remote_lock = threading.Lock()
        
    def __del__(self):
        self.close()
        
    def __cb_stx(self, remote):
        self.sendTo(self.STX_ACK, remote)
        self.appendRemote(remote)
        self.__cb_enter(self, remote, *self.__cb_enter_args)

    def __cb_stx_ack(self, remote):
        self.appendRemote(remote)
        self.__cb_enter(self, remote, *self.__cb_enter_args)
        
    def __cb_etx(self, remote):
        self.sendTo(self.ETX_ACK, remote)
        self.removeRemote(remote)        
        self.__cb_leave(self, remote, *self.__cb_leave_args)
    
    def __cb_etx_ack(self, remote):
        self.__ack_flags -= 1
        self.removeRemote(remote)
        self.__cb_leave(self, remote, *self.__cb_leave_args)
        if not self.__ack_flags:
            self.__wait_event.set()

    def __cb_recv_loop(self):
        message = Message()
        sessoin_funcs = {self.STX:self.__cb_stx, self.STX_ACK:self.__cb_stx_ack, self.ETX:self.__cb_etx, self.ETX_ACK:self.__cb_etx_ack}
        
        while self.__is_receiving:
            try:
                message.payload, message.remote = self.recvfrom(self.__recv_size)
            except (BlockingIOError, ConnectionResetError):
                continue

            if message.payload in (self.STX, self.STX_ACK, self.ETX, self.ETX_ACK):
                sessoin_funcs[message.payload](message.remote)
                continue

            if self.__recv_unpickling:
                try:
                    message.payload = pickle.loads(message.payload)
                except:
                    pass
            
            self.__cb_recv(self, message, *self.__cb_recv_args)
    
    def onEnter(self, func, *args):
        self.__cb_enter = func
        self.__cb_enter_args = args
    
    def onLeave(self, func, *args):
        self.__cb_leave = func
        self.__cb_leave_args = args
    
    def onRecv(self, func, *args, **kwargs):                    
        self.__cb_recv = func
        self.__cb_recv_args = args

        try:
            self.__recv_size = kwargs.pop('size')
        except KeyError:
            self.__recv_size = self.MAX_PAYLOAD_SIZE
        
        try:
            self.__recv_unpickling = kwargs.pop('unpickling')
        except KeyError:
            self.__recv_unpickling = False
        
    def loopStart(self, trigger=True):
        if self.__recv_thread: return
        
        self.__wait_event = threading.Event()
        self.__ack_flags = None
        
        if trigger:
            self.sendTo(self.STX) #All remote
            self.remote.clear()
            
        self.__is_receiving = True
        self.__recv_thread = threading.Thread(target=self.__cb_recv_loop, daemon=True)
        self.__recv_thread.start()        

    def loopStopWait(self, value):
        self.__ack_flags = value
        
    def loopStop(self, timeout=2):
        if not self.__recv_thread: return
        
        self.__wait_event.clear()
        
        if not self.__ack_flags:
            self.__ack_flags = len(self.remote)
            
        if self.__ack_flags:
            self.sendTo(self.ETX) #All remote
            
            t0 = time.time()
            while not self.__wait_event.wait(self.WAIT_EVENT_DELAY):
                if time.time() - t0 > timeout:
                    break

        self.__is_receiving = False
        self.__recv_thread.join()
        self.__recv_thread = None

    def loopForeverCancel(self, *args):
        self.__wait_event.set()
        
    def loopForever(self, timeout=2, **args):
        self.loopStart()

        self.__wait_event.clear()  
        signal.signal(signal.SIGINT, self.loopForeverCancel)
        
        while not self.__wait_event.wait(self.WAIT_EVENT_DELAY):
            pass
        
        self.loopStop(timeout)
        
    def recvFrom(self, size=MAX_PAYLOAD_SIZE, unpickling=False, timeout=None):
        message = Message()
        
        try:
            message.payload, message.remote = self.recvfrom(size)
        except (BlockingIOError, ConnectionResetError):
            if timeout:
                ready_to_read, ready_to_write, in_error = select.select([self], [], [], timeout)
                if self in ready_to_read:
                    message.payload, message.remote = self.recvfrom(size)
                else:
                    return None
                        
            else:
                return None

        if message.payload in (self.STX, self.STX_ACK, self.ETX, self.ETX_ACK):
            return None
            
        if unpickling:
            try:
                message.payload = pickle.loads(message.payload)
            except:
                pass
        
        return message
    
    def sendTo(self, payload, remote=None):
        if not isinstance(payload, bytes):
            payload = pickle.dumps(payload)
        
        if remote:
            return self.sendto(payload, remote) == len(payload)
        elif not self.remote:
            return False
        
        self.__remote_lock.acquire()
        ret = [False] * len(self.remote)
        for i, remote in enumerate(self.remote):
            ret[i] = self.sendto(payload, remote) != len(payload)
        self.__remote_lock.release()
        return all(ret)
        
    def close(self):
        self.remote.clear()
        self.group.clear()
        super().close()

    @property
    def local(self):
        return self.__local

    @local.setter
    def local(self, addr):
        self.__local = addr

    @property
    def remote(self):
        return self.__remote_set

    def appendRemote(self, remote):
        self.__remote_lock.acquire()        
        self.remote.add(remote)
        self.__remote_lock.release()

    def removeRemote(self, remote):
        self.__remote_lock.acquire()
        try:
            self.remote.remove(remote)
        except KeyError:
            pass
        self.__remote_lock.release()

    def setTTL(self, ttl):
        self.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    def getTTL(self):
        self.getsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL)

    def appendMembership(self, group):
        mreq = struct.pack("4sL", socket.inet_aton(group), socket.INADDR_ANY)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def removeMembership(self, group):
        mreq = struct.pack("4sL", socket.inet_aton(group), socket.INADDR_ANY)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)

    def sendToGroup(self, payload, group=None):
        if not isinstance(payload, bytes):
            payload = pickle.dumps(payload)
        
        if group:
            return self.sendto(payload, group) == len(payload)
        elif not self.group:
            return False
        
        ret = [False] * len(self.group)
        for i, group in enumerate(self.group):
            ret[i] = self.sendto(payload, group) != len(payload)
        return all(ret)

    @property
    def group(self):
        return self.__group_set
            
    def appendGroup(self, group):
        self.group.add(group)

    def removeGroup(self, group):
        try:
            self.group.remove(group)
        except KeyError:
            pass


class UDPServer(UDP):    
    def __init__(self, iface=UDP.DEFAULT_INTERFACE, port=UDP.DEFAULT_PORT):
        super().__init__()
        
        self.bind((iface, port))
        self.local = ([adapter.ips[0].ip for adapter in ifaddr.get_adapters() if not "172" in adapter.ips[0].ip], port)

    def loopStart(self):
        super().loopStart(False)

    def clearRecvBuffer(self):
        while True:
            try:
                self.recvfrom(self.MAX_PAYLOAD_SIZE)
            except BlockingIOError:
                break
                

class UDPClient(UDP):    
    def __init__(self, ip=UDP.DEFAULT_SERVER_IP, port=UDP.DEFAULT_PORT):
        super().__init__()
        
        if platform.system() == "Windows": #Proceed only after sending one packet
            self.sendTo(b'', (ip, 0)) #dummpy send
            
        self.local = (socket.gethostbyname(socket.gethostname()), self.getsockname()[1]) 
        self.appendRemote((ip, port))   


class MulticastReceiver(UDPServer):
    def __init__(self, group=UDP.DEFAULT_GROUP, port=UDP.DEFAULT_PORT, is_all_recv=False):        
        iface = UDP.DEFAULT_INTERFACE if is_all_recv else group
        super().__init__(iface, port)

        self.appendGroup((group, port))
        self.appendMembership(group)

    def close(self):
        for group in self.group:
            self.removeMembership(group[0])
        super().close()     


class MulticastSender(UDPClient):
    def __init__(self, group=UDP.DEFAULT_GROUP, port=UDP.DEFAULT_PORT, ttl=UDP.DEFAULT_TTL):
        super().__init__(group, port)
        self.remote.clear()
        
        self.appendGroup((group, port))        
        self.setTTL(ttl)
    
    sendTo = lambda self, payload, group=None: self.sendToGroup(payload, group)