class SlidingWindow:
    def __init__(self, packets):
        self.packets = packets
        self.window_size = window_size
        self.window_index = 0
        self.__calculate_window()

    def slide(self):
        self.window_index += 1
        self.__calculate_window

    def __calculate_window(self):
        if self.window_index + self.window_size < len(self.packets):
            self.window = self.packets[self.window_index : self.window_index + self.window_size]
        else:
            self.window = self.packets[self.window_index : len(self.packets)]
