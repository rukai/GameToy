class Memory:
    def __init__(self, rom, header):
        self.header = header
        self.rom = rom
        self.external_ram = [0 for i in range(self.header.ram_size)]
        self.internal_ram = [0 for i in range(0x4000 * 2)]
        self.vram = [0 for i in range(0x2000)]
        self.oam = [0 for i in range(0xA0)]
        self.hram = [0 for i in range(0x80)]
        self.rom_bank = 0
        self.cart_ram_bank = 0
        self.enable_cart_ram = False
        self.rom_banking_mode = True
        
        if self.header.mbc == "MBC1":
            self.writeToROM = self.writeToMBC1
            self.rom_bank = 1
        elif self.header.mbc == "MBC2":
            self.writeToROM = self.writeToMBC2
        elif self.header.mbc == "MBC3":
            self.writeToROM = self.writeToMBC3
        elif self.header.mbc == "MBC4":
            self.writeToROM = self.writeToMBC4
        elif self.header.mbc == "MBC5":
            self.writeToROM = self.writeToMBC5
        

    def setupIO(self, lcdc, interrupts, timer, sound, link):
        self.io_read = {
            0x0F: interrupts.readIF,
            0x01: link.dummy,
            0x02: link.dummy,
            0x04: timer.readDIV,
            0x05: timer.readTIMA,
            0x06: timer.readTMA,
            0x07: timer.readTAC,
            0x10: sound.dummy,
            0x11: sound.dummy,
            0x12: sound.dummy,
            0x13: sound.dummy,
            0x14: sound.dummy,
            0x16: sound.dummy,
            0x17: sound.dummy,
            0x18: sound.dummy,
            0x19: sound.dummy,
            0x1A: sound.dummy,
            0x1B: sound.dummy,
            0x1C: sound.dummy,
            0x1D: sound.dummy,
            0x1E: sound.dummy,
            0x20: sound.dummy,
            0x21: sound.dummy,
            0x22: sound.dummy,
            0x23: sound.dummy,
            0x24: sound.dummy,
            0x25: sound.dummy,
            0x26: sound.dummy,
            0x30: sound.dummy,
            0x26: sound.readNR52,
            0x40: lcdc.readLCDC,
            0x41: lcdc.readSTAT,
            0x42: lcdc.readSCY,
            0x43: lcdc.readSCX,
            0x44: lcdc.readLY,
            0x45: lcdc.readLYC,
            0x47: lcdc.readBGP,
            0x48: lcdc.readOBP0,
            0x49: lcdc.readOBP1,
            0x4A: lcdc.readWY,
            0x4B: lcdc.readWX,
            0xFF: interrupts.readIE,
        }

        self.io_write = {
            0x0F: interrupts.writeIF,
            0x01: link.dummy,
            0x02: link.dummy,
            0x04: timer.writeDIV,
            0x05: timer.writeTIMA,
            0x06: timer.writeTMA,
            0x07: timer.writeTAC,
            0x10: sound.dummy,
            0x11: sound.dummy,
            0x12: sound.dummy,
            0x13: sound.dummy,
            0x14: sound.dummy,
            0x16: sound.dummy,
            0x17: sound.dummy,
            0x18: sound.dummy,
            0x19: sound.dummy,
            0x1A: sound.dummy,
            0x1B: sound.dummy,
            0x1C: sound.dummy,
            0x1D: sound.dummy,
            0x1E: sound.dummy,
            0x20: sound.dummy,
            0x21: sound.dummy,
            0x22: sound.dummy,
            0x23: sound.dummy,
            0x24: sound.dummy,
            0x25: sound.dummy,
            0x26: sound.dummy,
            0x30: sound.dummy,
            0x26: sound.writeNR52,
            0x40: lcdc.writeLCDC,
            0x41: lcdc.writeSTAT,
            0x42: lcdc.writeSCY,
            0x43: lcdc.writeSCX,
            0x44: lcdc.writeLY,
            0x45: lcdc.writeLYC,
            0x47: lcdc.writeBGP,
            0x48: lcdc.writeOBP0,
            0x49: lcdc.writeOBP1,
            0x4A: lcdc.writeWY,
            0x4B: lcdc.writeWX,
            0xFF: interrupts.writeIE,
        }

        self.loadIOvalues()

    def loadIOvalues(self):
        self.write(0xFF05, 0x00)
        self.write(0xFF06, 0x00)
        self.write(0xFF07, 0x00)
        #self.write(0xFF10, 0x80)
        #self.write(0xFF11, 0xBF)
        #self.write(0xFF12, 0xF3)
        #self.write(0xFF14, 0xBF)
        #self.write(0xFF16, 0x3F)
        #self.write(0xFF17, 0x00)
        #self.write(0xFF19, 0xBF)
        #self.write(0xFF1A, 0xFF)
        #self.write(0xFF1B, 0x00)
        #self.write(0xFF1C, 0x00)
        #self.write(0xFF1E, 0xBF)
        #self.write(0xFF20, 0x77)
        #self.write(0xFF25, 0xF3)
        self.write(0xFF26, 0xF1)
        self.write(0xFF40, 0x91)
        self.write(0xFF42, 0x00)
        self.write(0xFF43, 0x00)
        self.write(0xFF45, 0x00)
        self.write(0xFF47, 0xFC)
        self.write(0xFF48, 0xFF)
        self.write(0xFF49, 0xFF)
        self.write(0xFF4A, 0x00)
        self.write(0xFF4B, 0x00)
        self.write(0xFFFF, 0x00)

    def read(self, location):
        if location < 0x4000: # 16KB ROM Bank 0
            return self.rom[location]

        elif location < 0x8000: # 16KB ROM Bank n
            bank_offset = self.rom_bank * 0x4000
            return self.rom[location - 0x4000 + bank_offset]

        elif location < 0xA000: # 8KB VRAM
            return self.vram[location - 0x8000]

        elif location < 0xC000: # 8KB External RAM Bank n
            bank_offset = self.cart_ram_bank * 0x4000
            ram_location = location - 0xA000 + bank_offset
            if ram_location < len(self.external_ram):
                return self.external_ram[ram_location]
            else:
                return 0

        elif location < 0xE000: # 4KB + 4KB Internal RAM Bank 0 + 1
            return self.internal_ram[location - 0xC000]

        elif location < 0xFE00: # Internal RAM echo
            return self.internal_ram[location - 0xE000]

        elif location < 0xFEA0: # 160B Sprite Attribute Table
            return self.oam[location - 0xFE00]

        elif location < 0xFF00: # Not usable
            return 0

        elif location < 0xFF80 or location == 0xFFFF: # I/O Ports
            io_location = location - 0xFF00
            if io_location in self.io_read:
                return self.io_read[io_location]()
            else:
                assert(False)

        elif location <= 0xFFFF: # 127B High ram
            return self.hram[location - 0xFF80]

        else:
            assert(False)

    def readSigned(self, location):
        value = self.read(location)
        if value & 0b10000000:
            value = value - 0b100000000
        return value

    def write(self, location, value):
        if location < 0x8000:
            self.writeToROM(location, value)

        elif location < 0xA000:
            self.vram[location - 0x8000] = value

        elif location < 0xC000:
            bank_offset = self.cart_ram_bank * 0x4000
            ram_location = location - 0xA000 + bank_offset
            if self.header.ram and ram_location < len(self.external_ram):
                if self.header.mbc == "MBC2":
                    value &= 0x0F
                self.external_ram[location - 0xA000 + bank_offset] = value
            else:
                return 0

        elif location < 0xE000:
            self.internal_ram[location - 0xC000] = value

        elif location < 0xFE00:
            self.internal_ram[location - 0xE000] = value

        elif location < 0xFEA0:
            self.oam[location - 0xFE00]

        elif location < 0xFF00:
            pass

        elif location < 0xFF80 or location == 0xFFFF:
            io_location = location - 0xFF00
            if io_location in self.io_write:
                self.io_write[io_location](value)
            else:
                assert(False)

        elif location < 0xFFFF:
            self.hram[location - 0xFF80] = value

        else:
            assert(False)

    def writeToROM(self, location, value):
        print("Cannot write to {}".format(self.header.mbc))
        assert(False)

    def writeToMBC1(self, location, value):
        if location < 0x2000: # Enable ram
            if (value & 0x0F) == 0x0A:
                self.enable_cart_ram = True
            else:
                self.enable_cart_ram = False

        elif location < 0x4000: # ROM bank lower bits
            bit_mask = 0b00011111
            lower_bits = value & bit_mask
            if lower_bits == 0:
                lower_bits = 1
            self.rom_bank = (self.rom_bank & ~bit_mask) | lower_bits

        elif location < 0x6000:
            bit_mask = 0b00000011
            if self.rom_banking_mode: # ROM bank higher bits
                higher_bits = value & bit_mask
                self.rom_bank = (self.rom_bank & 0b10011111) | (higher_bits << 5)
            else: #RAM bank
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

    def display(self):
        print("------------------------------------------------")
        print("Memory dump:")
        print("ROM bank:", self.rom_bank)
        print("Cart RAM bank:", self.cart_ram_bank)
        print("Cart RAM enabled:", self.enable_cart_ram)
        print("Banking mode:", "ROM" if self.rom_banking_mode else "RAM")
        for line_number in range(0x0, 0x10000, 0x10):
            line = hex(line_number)[2:].zfill(4) + ": "
            # skip I/O ports until they are all handled
            if line_number >= 0xFF00 and line_number < 0xFF80:
                line += "0000 " * 8
            else:
                for j in range(line_number, line_number + 0x10, 2):
                    line += hex(self.read(j  ))[2:].zfill(2)
                    line += hex(self.read(j+1))[2:].zfill(2) + " "
            print(line)
