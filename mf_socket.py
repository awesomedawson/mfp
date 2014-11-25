from mf_packet import MFPacket
from io_loop import IOLoop
from sliding_window import SlidingWindow

class MFSocket:
    def __init__(self, port_number, buffer_size = 128):
        self.sequence_number = 0
        self.port_number = port_number
        self.io_loop = IOLoop()

    def mf_bind(self, address):
        self.io_loop.socket.bind(address)

    def mf_listen(self, window_size = 10):
        pass

    def mf_accept(self):
        syn_received = False
        ack_received = False
        self.io_loop.start()

        while not syn_received or not ack_received:
            packet, address = self.io_loop.receive_queue.get()

            if syn_received:
                if packet.ack:
                    ack_received = True
            else:
                if packet.syn:
                    syn_received = True

                    # TODO retransmit timer
                    self.io_loop.send_queue.put((MFPacket(
                        self.port_number,
                        address[1],
                        ack_number = packet.sequence_number + 1,
                        ack = True,
                        syn = True
                    ), address))

    def mf_connect(self, address):
        syn_ack_received = False
        self.io_loop.start()

        # TODO retransmit timer
        self.io_loop.send_queue.put((MFPacket(
            self.port_number,
            address[1],
            syn = True
        ), address))

        while not syn_ack_received:
            packet, address = self.io_loop.receive_queue.get()

            if packet.syn and packet.ack:
                syn_ack_received = True

                # TODO retransmit timer
                self.io_loop.send_queue.put((MFPacket(
                    self.port_number,
                    address[1],
                    ack_number = packet.sequence_number + 1,
                    sequence_number = 1,
                    ack = True
                ), address))

    def mf_write(self, data):
        pass

    def mf_close(self):
        pass

    def __read_packet():
        data, address = self.sock.recvfrom(self.buffer_size)
        data = map(ord, data.encode('utf8'))
        return (MFPacket.parse(data), address)
