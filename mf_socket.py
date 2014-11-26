from mf_packet import MFPacket
from io_loop import IOLoop
from sliding_window import SlidingWindow
from retransmit_timer import RetransmitTimer
import Queue
import time

class MFSocket:
    def __init__(self, window_size = 10):
        self.window_size = window_size
        self.window = {}
        self.sequence_number = 0
        self.retransmit_timer = RetransmitTimer()
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
                syn_packet, self.destination = self.io_loop.receive_queue.get(True, 1)
            except Queue.Empty:
                continue

            syn_received = self.__verify_syn(syn_packet, self.destination)

        # send syn/ack
        syn_ack_packet = MFPacket(
            self.port_number,
            self.destination[1],
            ack_number = syn_packet.sequence_number + 1,
            ack = True,
            syn = True
        )
        self.io_loop.send_queue.put((syn_ack_packet, self.destination))

        # wait for ack, retransmit on timeout
        while not ack_received:
            try:
                ack_packet, address = self.io_loop.receive_queue.get(True, 1)
            except Queue.Empty:
                syn_ack_packet.frequency += 1
                syn_ack_packet.recalculate_checksum()
                self.io_loop.send_queue.put((syn_ack_packet, self.destination))
                continue

            ack_received = self.__verify_ack(ack_packet, address, syn_ack_packet.sequence_number)

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
                syn_ack_packet, address = self.io_loop.receive_queue.get(True, 1)
            except Queue.Empty:
                syn_packet.frequency += 1
                syn_packet.recalculate_checksum()
                self.io_loop.send_queue.put((syn_packet, self.destination))
                continue

            syn_ack_received = self.__verify_syn_ack(syn_ack_packet, address, syn_packet.sequence_number)

        # send ack
        ack_packet = MFPacket(
            self.port_number,
            self.destination[1],
            ack_number = syn_ack_packet.sequence_number + 1,
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
        window = SlidingWindow(packets, self.window_size)

        last_sent = time.time()
        time_remaining = self.retransmit_timer.timeout
        for data_packet in window.window:
            self.io_loop.send_queue.put((data_packet, self.destination))

        while not window.is_empty():
            try:
                # wait for incoming packet
                ack_packet, address = self.io_loop.receive_queue.get(True, time_remaining)
            except Queue.Empty:
                # timeout, go back n
                last_sent = time.time()
                time_remaining = self.retransmit_timer.timeout
                for data_packet in window.window:
                    data_packet.frequency += 1
                    data_packet.recalculate_checksum()
                    self.io_loop.send_queue.put((data_packet, self.destination))

                continue

            # if still getting syn/ack, retransmit ack
            if self.__verify_syn_ack(ack_packet, address, 1):
                ack_packet = MFPacket(
                    self.port_number,
                    self.destination[1],
                    ack_number = ack_packet.sequence_number + 1,
                    sequence_number = 2,
                    ack = True
                )
                self.io_loop.send_queue.put((ack_packet, self.destination))
            # if first packet in pipeline is acknowledged, slide the window
            elif self.__verify_ack(ack_packet, address, window.window[0].sequence_number):
                self.retransmit_timer.update(ack_packet.frequency, time.time() - last_sent)
                window.slide()
            # otherwise, update time remaining
            else:
                time_remaining -= time.time() - last_sent

    def mf_read(self):
        fin_received = False
        packets = {}
        frequencies = {}

        # until connection is closed, read data
        while not fin_received:
            try:
                data_packet, address = self.io_loop.receive_queue.get(True, 1)
            except Queue.Empty:
                continue

            if address == self.destination:
                if data_packet.fin:
                    fin_received = True
                else:
                    if frequencies.get(data_packet.sequence_number):
                        frequencies[data_packet.sequence_number] += 1
                    else:
                        frequencies[data_packet.sequence_number] = 1

                    packets[data_packet.sequence_number] = data_packet
                    ack_packet = MFPacket(
                        self.port_number,
                        self.destination[1],
                        sequence_number = self.sequence_number,
                        frequency = frequencies[data_packet.sequence_number],
                        ack = True,
                        ack_number = data_packet.sequence_number + 1
                    )
                    self.io_loop.send_queue.put((ack_packet, self.destination))
                    self.sequence_number += 1

        self.__close(data_packet.sequence_number + 1)

        return ''.join(map(lambda packet: packet.payload, map(lambda sequence_number: packets[sequence_number], sorted(packets.keys()))))

    def mf_close(self):
        fin_ack_received = False

        fin_packet = MFPacket(
            self.port_number,
            self.destination[1],
            sequence_number = self.sequence_number,
            fin = True
        )
        self.io_loop.send_queue.put((fin_packet, self.destination))
        self.sequence_number += 1

        while not fin_ack_received:
            try:
                fin_ack_packet, address = self.io_loop.receive_queue.get(True, 1)
            except Queue.Empty:
                break

            if address == self.destination and fin_ack_packet.fin and fin_ack_packet.ack:
                ack_packet = MFPacket(
                    self.port_number,
                    self.destination[1],
                    sequence_number = self.sequence_number,
                    ack = True,
                    ack_number = fin_ack_packet.sequence_number
                )
                self.io_loop.send_queue.put((ack_packet, self.destination))
                self.sequence_number += 1

    def __close(self, ack_number):
        ack_received = False

        fin_ack_packet = MFPacket(
            self.port_number,
            self.destination[1],
            sequence_number = self.sequence_number,
            fin = True,
            ack = True,
            ack_number = ack_number
        )
        self.io_loop.send_queue.put((fin_ack_packet, self.destination))
        self.sequence_number += 1

        while not ack_received:
            try:
                ack_packet, address = self.io_loop.receive_queue.get(True, 1)
            except Queue.Empty:
                break

            ack_received = self.__verify_ack(ack_packet, address, fin_ack_packet.sequence_number)

    def __verify_syn(self, packet, address):
        return address == self.destination and packet.syn

    def __verify_ack(self, packet, address, sequence_number):
        return address == self.destination and packet.ack and packet.ack_number - 1 == sequence_number

    def __verify_syn_ack(self, packet, address, sequence_number):
        return address == self.destination and packet.syn and packet.ack and packet.ack_number - 1 == sequence_number
