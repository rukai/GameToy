class LCDC:
    def __init__(self, mem):
        self.mem = mem

    def update(self):
        #temporary kludge to get LA out of an infinite loop
        value = (self.mem.get(0xFF44) + 1) % 154
        self.mem.set(0xFF44, value)
