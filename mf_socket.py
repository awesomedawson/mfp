from mf_packet import MFPacket
from io_loop import IOLoop
from sliding_window import SlidingWindow
import Queue
import time

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
                self.io_loop.send_queue.put((syn_packet, self.destination))
                continue

            syn_ack_received = address == self.destination and packet.syn and packet.ack

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
            if start + payload_size <= len(data):
                payload = data[start : start + payload_size]
            else:
                payload = data[start :]

            data_packet = MFPacket(
                self.port_number,
                self.destination[1],
                sequence_number = self.sequence_number,
                payload = payload
            )
            packets.append(data_packet)
            self.sequence_number += 1
            start += payload_size

        # populate window and send all packets
        # TODO handle dropped ack during handshake
        window = SlidingWindow(packets, self.window_size)

        for data_packet in window.window:
            self.io_loop.send_queue.put((data_packet, self.destination))

        while not window.is_empty():
            try:
                # wait for incoming packet
                ack_packet, address = self.io_loop.receive_queue.get(True, 1)
            except Queue.Empty:
                # timeout, go back n
                for data_packet in window.window:
                    self.io_loop.send_queue.put((data_packet, self.destination))

                continue

            # if first packet in pipeline is acknowledged, slide the window
            if ack_packet.ack and ack_packet.ack_number - 1 == window.window[0].sequence_number:
                window.slide()

    def mf_read(self):
        fin_received = False
        packets = {}

        while not fin_received:
            try:
                data_packet, address = self.io_loop.receive_queue.get(True, 1)
            except Queue.Empty:
                continue

            if address == self.destination:
                if data_packet.fin:
                    fin_received = True
                else:
                    packets[data_packet.sequence_number] = data_packet
                    ack_packet = MFPacket(
                        self.port_number,
                        self.destination[1],
                        sequence_number = self.sequence_number,
                        ack = True,
                        ack_number = data_packet.sequence_number + 1
                    )
                    self.io_loop.send_queue.put((ack_packet, self.destination))
                    self.sequence_number += 1

        # TODO close connection

        return ''.join(map(lambda packet: packet.payload, map(lambda sequence_number: packets[sequence_number], sorted(packets.keys()))))

    def mf_close(self):
        fin_packet = MFPacket(
            self.port_number,
            self.destination[1],
            sequence_number = self.sequence_number,
            fin = True
        )
        self.io_loop.send_queue.put((fin_packet, self.destination))
        self.sequence_number += 1
