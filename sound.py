class Sound:
    def __init__(self):
        self.enable       = False
        self.enable_chan4 = False
        self.enable_chan3 = False
        self.enable_chan2 = False
        self.enable_chan1 = False

    def readNR52(self):
        value = int(self.enable) << 7
        value = int(self.enable_chan4) << 3
        value = int(self.enable_chan3) << 2
        value = int(self.enable_chan2) << 1
        value = int(self.enable_chan1)

    def writeNR52(self, value):
        self.enable = bool(value & 0b10000000)
        # individual channels are not modified.

    def dummy(self, foo=0):
        return 0
