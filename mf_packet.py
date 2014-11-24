import math
import hashlib

class MFPacket:
    def __init__(
        self,
        source_port,
        destination_port,
        payload = '',
        sequence_number = 0,
        ack_number = 0,
        frequency = 1,
        ack = False,
        syn = False,
        fin = False,
        checksum = None,
        window_size = 1024
    ):
        self.source_port = source_port
        self.destination_port = destination_port
        self.sequence_number = sequence_number
        self.ack_number = ack_number
        self.frequency = frequency
        self.ack = ack
        self.syn = syn
        self.fin = fin
        self.data_offset = int(math.ceil(1.0 * len(payload) / 4))
        self.checksum = 0
        self.window_size = window_size
        self.payload = payload

        checksum_algorithm = hashlib.md5()
        checksum_algorithm.update(self.serialize())
        self.checksum = int(checksum_algorithm.hexdigest(), 16) & int(math.pow(2, 16) - 1)

        if checksum and checksum != self.checksum:
            raise Exception

    @classmethod
    def parse(self, data):
        raw_packet = map(ord, data)
        return MFPacket(
            (raw_packet[0] << 8) | raw_packet[1],
            (raw_packet[2] << 8) | raw_packet[3],
            payload = raw_packet[20 : 20 + raw_packet[13] * 4],
            sequence_number = raw_packet[4] << 24 | raw_packet[5] << 16 | raw_packet[6] << 8 | raw_packet[7],
            ack_number = raw_packet[8] << 24 | raw_packet[9] << 16 | raw_packet[10] << 8 | raw_packet[11],
            frequency = raw_packet[12] >> 3,
            ack = (raw_packet[12] & 4) == 4,
            syn = (raw_packet[12] & 2) == 2,
            fin = (raw_packet[12] & 1) == 1,
            checksum = (raw_packet[14] << 8) | raw_packet[15],
            window_size = raw_packet[16] << 24 | raw_packet[17] << 16 | raw_packet[18] << 8 | raw_packet[19],
        )

    def serialize(self):
        BIT_MASK_1 = 255 << 24
        BIT_MASK_2 = 255 << 16
        BIT_MASK_3 = 255 << 8
        BIT_MASK_4 = 255

        words = [
            (self.source_port << 16) + (self.destination_port),
            self.sequence_number,
            self.ack_number,
            (self.frequency << 27) + (int(self.ack) << 26) + (int(self.syn) << 25) + (int(self.fin) << 24) + (self.data_offset << 16) + self.checksum,
            self.window_size
        ]
        byte_array = []

        for word in words:
            byte_array.append((word & BIT_MASK_1) >> 24)
            byte_array.append((word & BIT_MASK_2) >> 16)
            byte_array.append((word & BIT_MASK_3) >> 8)
            byte_array.append(word & BIT_MASK_4)

        byte_array = bytearray(byte_array) + self.payload
        return ''.join(map(chr, byte_array))
