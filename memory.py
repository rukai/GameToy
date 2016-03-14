class Memory:
    def __init__(self, rom, header):
        self.rom    = rom
        self.ram    = [0 for i in range(0x10000)] # Quick hack
        self.header = header

        self.setDefaultValues()

    def setDefaultValues(self):
        self.set(0xFF05, 0x00)
        self.set(0xFF06, 0x00)
        self.set(0xFF07, 0x00)
        self.set(0xFF10, 0x80)
        self.set(0xFF11, 0xBF)
        self.set(0xFF12, 0xF3)
        self.set(0xFF14, 0xBF)
        self.set(0xFF16, 0x3F)
        self.set(0xFF17, 0x00)
        self.set(0xFF19, 0xBF)
        self.set(0xFF1A, 0xFF)
        self.set(0xFF1B, 0x00)
        self.set(0xFF1C, 0x00)
        self.set(0xFF1E, 0xBF)
        self.set(0xFF20, 0x77)
        self.set(0xFF25, 0xF3)
        self.set(0xFF26, 0xF1)
        self.set(0xFF40, 0x91)
        self.set(0xFF42, 0x00)
        self.set(0xFF43, 0x00)
        self.set(0xFF45, 0x00)
        self.set(0xFF47, 0xFC)
        self.set(0xFF48, 0xFF)
        self.set(0xFF49, 0xFF)
        self.set(0xFF4A, 0x00)
        self.set(0xFF4B, 0x00)
        self.set(0xFFFF, 0x00)


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
