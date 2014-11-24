from threading import Thread
from Queue import Queue
from receive_queue import ReceiveQueue
from mf_packet import MFPacket
import socket

class IOLoop(Thread):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.daemon = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_queue = Queue()
        self.receive_queue = ReceiveQueue()
        self.socket.settimeout(0.1)
        self.exit = False

    def run(self):
        while True:
            if self.exit:
                self.exit()

            try:
                packet, address = self.send_queue.get_nowait()
                self.socket.sendto(packet.serialize(), address)
            except:
                pass

            try:
                packet, address = self.socket.recvfrom()

                # TODO make sure valid packet
                packet = MFPacket.parse(packet)
                self.receive_queue.put((packet, address))
            except:
                pass
