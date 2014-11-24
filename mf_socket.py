from mf_packet import MFPacket
from io_loop import IOLoop
from sliding_window import SlidingWindow

class MFSocket:
    def __init__(self, buffer_size = 128):
        self.sequence_number = 0
        self.io_loop = IOLoop()

    def mf_bind(self, address):
        self.address = address

    def mf_listen(self, window_size = 10):
        self.send_window = SlidingWindow(window_size)
        self.receive_window = SlidingWindow(window_size)

    def mf_accept(self):
        syn_received = False
        ack_received = False
        self.io_loop.start()

        while not syn_received or not ack_received:
            packet, address = self.io_loop.receive_queue.get().packet

            if syn_received:
                if packet.ack:
                    ack_received = True
            else:
                if packet.syn:
                    syn_received = True
                    self.io_loop.send_queue.put(MFPacket(
                        self.address[1],
                        address[1],
                        ack_number = packet.sequence_number + 1,
                        ack = True,
                        syn = True
                    ))

    def mf_connect(self, address):
        # send syn
        packet = MFPacket(
            self.port_number,
            port_number,
            syn = True
        )
        self.sock.sendto(packet.serialize, address)
        self.sequence_number += 1

        # wait for syn/ack
        packet, address = self.__read_packet()

        while not packet.ack or not packet.syn:
            packet, address = self.__read_packet()

        # send ack
        packet = MFPacket(
            self.port_number,
            port_number,
            sequence_number = self.sequence_number,
            ack_number = packet.sequence_number + 1,
            ack = True
        )
        self.sock.sendto(packet.serialize, address)
        self.sequence_number += 1

    def mf_write(self, data):
        pass

    def mf_close(self):
        pass

    def __read_packet():
        data, address = self.sock.recvfrom(self.buffer_size)
        data = map(ord, data.encode('utf8'))
        return (MFPacket.parse(data), address)
