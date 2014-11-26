class RetransmitTimer:
    def __init__(self):
        self.timeout = 6
        self.threshold = .75

    def update(self, rtt, frequency):
        true_rtt = 1.0 * rtt / frequency
        self.timeout = self.threshold * self.timeout + (1 - self.threshold) * true_rtt
