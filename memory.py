class Memory:
    def __init__(self, rom, header):
        self.rom    = rom
        self.ram    = [0 for i in range(0x10000)] # Quick hack
        self.header = header

    def get(self, location):
        if location < 0x4000:
            return self.rom[location]
        else:
            return self.ram[location - 0x4000]

    def getSigned(self, location):
        value = self.get(location)
        if value & 0b10000000:
            value = value - 0b100000000
        return value


    def set(self, location, value):
        if location < 0x4000:
            assert(False)
        else:
            self.ram[location - 0x4000] = value
