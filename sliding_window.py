class SlidingWindow:
    def __init__(self, window_size = 10):
        self.window = []
        self.window_size = window_size
        self.beginning_sequence_number = 0
        self.ending_sequence_number = window_size - 1

    def slide(self):
        num_acknowledged = 0

        for element in window:
            if element.acknowledged:
                num_acknowledged += 1

        self.beginning_sequence_number += num_acknowledged
        self.ending_sequence_number += num_acknowledged
        self.window = window[num_acknowledged : len(window)]

    def add(self, packet):
        if len(self.window) == self.window_size:
            return False

        element = WindowElement(packet)

        if len(window) == 0:
            window.append(element)
        elif (window[0].packet.sequence_number > packet.sequence_number):
            window = [element] + window
        elif (window[-1].packet.sequence_number < packet.sequence_number):
            window = window + [element]
        else:
            for i in range(len(window)):
                if window[i].packet.sequence_number > packet.sequence_number:
                    window = window[0 : i] + [element] + window[i : len(window)]

        self.ending_sequence_number += 1
        return True
