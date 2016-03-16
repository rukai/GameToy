from header import Header

class Memory:
    def __init__(self, rom):
        self.header = Header(rom)
        self.rom = rom
        self.external_ram = [0 for i in range(self.header.ram_banks * 0x4000)]
        self.internal_ram = [0 for i in range(0x4000 * 2)]
        self.vram = [0 for i in range(0x2000)]
        self.oam = [0 for i in range(0xA0)]
        self.hram = [0 for i in range(0x100)]
        self.rom_bank = 1
        self.cart_ram_bank = 1
        self.enable_ram = False
        self.rom_banking_mode = True
        
        if self.header.mbc == "MBC1":
            self.writeToROM = self.writeToMBC1
        elif self.header.mbc == "MBC2":
            self.writeToROM = self.writeToMBC2
        elif self.header.mbc == "MBC3":
            self.writeToROM = self.writeToMBC3
        elif self.header.mbc == "MBC4":
            self.writeToROM = self.writeToMBC4
        elif self.header.mbc == "MBC5":
            self.writeToROM = self.writeToMBC5

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
        if location < 0x4000: # 16KB ROM Bank 0
            return self.rom[location]

        elif location < 0x8000: # 16KB ROM Bank n
            bank_offset = self.rom_bank * 0x4000
            return self.rom[location - 0x4000 + bank_offset]

        elif location < 0xA000: # 8KB VRAM
            return self.vram[location - 0x8000]

        elif location < 0xC000: # 8KB External RAM Bank n
            bank_offset = self.cart_ram_bank * 0x4000
            return self.external_ram[location - 0xA000 + bank_offset]

        elif location < 0xE000: # 4KB + 4KB Internal RAM Bank 0 + 1
            return self.internal_ram[location - 0xC000]

        elif location < 0xFE00: # Internal RAM echo
            return self.internal_ram[location - 0xE000]

        elif location < 0xFEA0: # 160B Sprite Attribute Table
            return self.oam[location - 0xFE00]

        elif location < 0xFF00: # Not usable
            assert(False)

        elif location <= 0xFFFF: #255B High ram
            return self.hram[location - 0xFF00]

        else:
            assert(False)

    def getSigned(self, location):
        value = self.get(location)
        if value & 0b10000000:
            value = value - 0b100000000
        return value

    def set(self, location, value):

        if location < 0x8000:
            self.writeToROM(location, value)
        elif location < 0xA000:
            self.vram[location - 0x8000] = value

        elif location < 0xC000:
            if self.header.ram:
                bank_offset = self.cart_ram_bank * 0x4000
                self.external_ram[location - 0xA000 + bank_offset] = value

        elif location < 0xE000:
            self.internal_ram[location - 0xC000] = value

        elif location < 0xFE00:
            self.internal_ram[location - 0xE000] = value

        elif location < 0xFEA0:
            self.oam[location - 0xFE00]

        elif location < 0xFF00:
            assert(False)

        elif location <= 0xFFFF:
            self.hram[location - 0xFF00] = value

    def writeToROM(self, location, value):
        print("Cannot write to {}".format(self.header.mbc))
        assert(False)

    def writeToMBC1(self, location, value):
        if location < 0x2000: # Enable ram
            if (value & 0x0F) == 0x0A:
                self.enable_ram = True
            else:
                self.enable_ram = False

        elif location < 0x4000: # ROM bank lower bits
            bit_mask = 0b0001111
            lower_bits = value & bit_mask
            if lower_bits == 0:
                lower_bits = 1
            self.rom_bank = (self.rom_bank & ~bit_mask) | lower_bits

        elif location < 0x6000: # ROM bank higher bits
            if self.rom_banking_mode:
                #TODO: Where do the 2 bits go? Should I >> 5
                bit_mask = 0b01100000
                higher_bits = value & bit_mask
                self.rom_bank = (self.rom_bank & ~bit_mask) | higher_bits
            else:
                bit_mask = 0b00000011
                bits = value & bit_mask
                self.ram_bank = (self.ram_bank & ~bit_mask) | bits

        elif location < 0x8000: # ROM/RAM mode select
            if value == 0:
                self.rom_banking_mode = True
            elif value == 1:
                self.rom_banking_mode = False
            else:
                assert(false)


    def writeToMBC2(self, location, value):
        assert(False)

    def writeToMBC3(self, location, value):
        assert(False)

    def writeToMBC4(self, location, value):
        assert(False)

    def writeToMBC5(self, location, value):
        assert(False)
