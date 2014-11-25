from mf_packet import MFPacket
from io_loop import IOLoop
from sliding_window import SlidingWindow
import Queue

class MFSocket:
    def __init__(self, window_size = 10):
        self.window_size = window_size
        self.window = {}
        self.sequence_number = 0
        self.io_loop = IOLoop()

    def mf_assign(self, port_number):
        self.port_number = port_number

    def mf_bind(self, address):
        self.port_number = address[1]
        self.io_loop.socket.bind(address)

    def mf_accept(self):
        syn_received = False
        ack_received = False

        self.io_loop.start()

        # wait for syn
        while not syn_received:
            try:
                packet, self.destination = self.io_loop.receive_queue.get(True, 1)
            except Queue.Empty:
                continue

            syn_received = packet.syn

        # send syn/ack
        syn_ack_packet = MFPacket(
            self.port_number,
            self.destination[1],
            ack_number = packet.sequence_number + 1,
            ack = True,
            syn = True
        )
        self.io_loop.send_queue.put((syn_ack_packet, self.destination))

        # wait for ack, retransmit on timeout
        while not ack_received:
            try:
                packet, address = self.io_loop.receive_queue.get(True, 1)
            except Queue.Empty:
                syn_ack_packet.frequency += 1
                self.io_loop.send_queue.put((syn_ack_packet, self.destination))
                continue

            ack_received = address == self.destination and packet.ack

    def mf_connect(self, address):
        self.destination = address
        syn_ack_received = False

        self.io_loop.start()

        # send syn
        syn_packet = MFPacket(
            self.port_number,
            self.destination[1],
            sequence_number = self.sequence_number,
            syn = True
        )
        self.io_loop.send_queue.put((syn_packet, self.destination))
        self.sequence_number += 1

        # wait for syn/ack, retransmit on timeout
        while not syn_ack_received:
            try:
                packet, address = self.io_loop.receive_queue.get(True, 1)
            except Queue.Empty:
                syn_packet.frequency += 1
                self.io_loop.send_queue.put((syn_packet, self.destination))
                continue

            syn_ack_received = packet.syn and packet.ack

        # send ack
        ack_packet = MFPacket(
            self.port_number,
            self.destination[1],
            ack_number = packet.sequence_number + 1,
            sequence_number = self.sequence_number,
            ack = True
        )
        self.io_loop.send_queue.put((ack_packet, self.destination))
        self.sequence_number += 1

    def mf_write(self, data):
        start = 0
        payload_size = 1024
        packets = []

        # chunk data into packets
        while start < len(data):
            if start + chunk_size <= len(data):
                payload = data[start : start + chunk_size]
            else:
                payload = data[start :]

            packet = MFPacket(
                self.port_number,
                self.destination[1],
                sequence_number = self.sequence_number,
                payload = payload
            )
            packets.append(packet)
            self.sequence_number += 1

        # populate window and send all packets
        window = SlidingWindow(packets, self.window_size)
        last_sent = time.time()

        for packet in window.window:
            self.io_loop.send_queue.put((packet, self.destination))

        # pipeline the remaining data
        retransmit_period = 1

        while len(window.window) > 0:
            try:
                # wait for incoming packet
                packet, address = self.io_loop.send_queue.get(True, retransmit_period)
            except Queue.Empty:
                # timeout, go back n
                last_sent = time.time()
                for packet in window.window:
                    self.io_loop.send_queue.put((packet, self.destination))

                continue

            # if first packet in pipeline is acknowledged, slide the window
            if packet.ack and packet.ack_number == window.window[0].sequence_number - 1:
                window.slide()
            # otherwise, continue with the timeout
            else:
                retransmit_period = time.time() - sent

    def mf_read(self):
        pass

    def mf_close(self):
        pass
