from threading import Thread
import Queue
from receive_queue import ReceiveQueue
from mf_packet import MFPacket
from mf_packet import ParseException
import socket

class IOLoop(Thread):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.daemon = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_queue = Queue.Queue()
        self.receive_queue = Queue.Queue()
        self.socket.settimeout(0.01)

    def run(self):
        while True:
            try:
                packet, address = self.send_queue.get(True, 0.1)
                self.socket.sendto(packet.serialize(), address)
            except Queue.Empty:
                pass

            try:
                packet, address = self.socket.recvfrom(4096)
                packet = MFPacket.parse(packet)
                self.receive_queue.put((packet, address))
            except (socket.timeout, ParseException):
                pass
