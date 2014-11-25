from threading import Lock, Condition

class ReceiveQueue:
    def __init__(self):
        self.queue = []
        self.next_sequence_number = 0
        self.mutex = Lock()
        self.not_full = Condition(self.mutex)
        self.next_element_available = Condition(self.mutex)

    def put(self, pair):
        self.not_full.acquire()

        try:
            self.queue.append(pair)
            self.queue.sort(key = lambda pair: pair[0].sequence_number)

            print self.queue[0][0].sequence_number
            print self.next_sequence_number
            if self.queue[0][0].sequence_number == self.next_sequence_number:
                self.next_element_available.notify()
        finally:
            self.not_full.release()

    def get(self):
        self.next_element_available.acquire()

        try:
            while len(self.queue) == 0 or self.queue[0][0].sequence_number != self.next_sequence_number:
                self.next_element_available.wait()

            pair = self.queue[0]
            self.queue = self.queue[1:]
            self.next_sequence_number += 1

            return pair
        finally:
            self.next_element_available.release()
