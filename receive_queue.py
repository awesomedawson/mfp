from threading import Lock, Condition
import time

class TimeoutException(Exception):
    pass

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

            if self.queue[0][0].sequence_number == self.next_sequence_number:
                self.next_element_available.notify()
        finally:
            self.not_full.release()

    def get(self, timeout = 1):
        self.next_element_available.acquire()
        then = time.time()
        wait_timeout = timeout

        try:
            while len(self.queue) == 0 or self.queue[0][0].sequence_number != self.next_sequence_number:
                self.next_element_available.wait(wait_timeout)
                now = time.time()
                if now - then > timeout:
                    raise TimeoutException
                else:
                    wait_timeout = wait_timeout - (then - now)

            pair = self.queue[0]
            self.queue = self.queue[1:]
            self.next_sequence_number += 1

            return pair
        finally:
            self.next_element_available.release()
