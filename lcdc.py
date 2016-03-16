class LCDC:
    def __init__(self, mem):
        self.mem = mem

    def update(self):
        #temporary kludge to get LA out of an infinite loop
        self.mem.set(0xFF44, 0x91)
