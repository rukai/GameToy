class Header:
    def __init__(self, rom, debug):
        self.cartridgeType(rom)
        self.ramInfo(rom)
        self.romInfo(rom)
        self.rom_size = len(rom)

        self.name = ""
        for byte in rom[0x0134:0x0149]:
            if byte != 0:
                self.name += chr(byte)

        self.japanese = True
        if(rom[0x014A] == 1):
            self.japanese = False
    
        if debug:
            self.display()

    def cartridgeType(self, rom):
        "Store cartridge hardware flags"

        self.cartridge_type = rom[0x0147]
        self.mbc = None
        self.ram = False
        self.battery = False
        self.timer = False
        self.rumble = False
        
        if self.cartridge_type == 0x00:
            self.mbc = "ROM"
        elif self.cartridge_type == 0x01:
            self.mbc = "MBC1"
        elif self.cartridge_type == 0x02:
            self.mbc = "MBC1"
            self.battery = True
        elif self.cartridge_type == 0x03:
            self.mbc = "MBC1"
            self.ram = True
            self.battery = True
        elif self.cartridge_type == 0x05:
            self.mbc = "MBC2"
        elif self.cartridge_type == 0x06:
            self.mbc = "MBC1"
            self.battery = True
        elif self.cartridge_type == 0x08:
            self.mbc = "ROM"
            self.ram = True
        elif self.cartridge_type == 0x09:
            self.mbc = "ROM"
            self.ram = True
            self.battery = True
        elif self.cartridge_type == 0x0B:
            self.mbc = "MMM01"
        elif self.cartridge_type == 0x0C:
            self.mbc = "MMM01"
            self.ram = True
        elif self.cartridge_type == 0x0D:
            self.mbc = "MMM01"
            self.ram = True
            self.battery = True
        elif self.cartridge_type == 0x0F:
            self.mbc = "MBC3"
            self.battery = True
            self.timer = True
        elif self.cartridge_type == 0x10:
            self.mbc = "MBC3"
            self.ram = True
            self.battery = True
            self.timer = True
        elif self.cartridge_type == 0x11:
            self.mbc = "MBC3"
        elif self.cartridge_type == 0x12:
            self.mbc = "MBC3"
            self.ram = True
        elif self.cartridge_type == 0x13:
            self.mbc = "MBC3"
            self.ram = True
            self.battery = True
        elif self.cartridge_type == 0x15:
            self.mbc = "MBC4"
        elif self.cartridge_type == 0x16:
            self.mbc = "MBC4"
            self.ram = True
        elif self.cartridge_type == 0x17:
            self.mbc = "MBC4"
            self.ram = True
            self.battery = True
        elif self.cartridge_type == 0x19:
            self.mbc = "MBC5"
        elif self.cartridge_type == 0x1A:
            self.mbc = "MBC5"
            self.ram = True
        elif self.cartridge_type == 0x1B:
            self.mbc = "MBC5"
            self.ram = True
            self.battery = True
        elif self.cartridge_type == 0x1C:
            self.mbc = "MBC5"
            self.rumble = True
        elif self.cartridge_type == 0x1D:
            self.mbc = "MBC5"
            self.ram = True
            self.rumble = True
        elif self.cartridge_type == 0x1E:
            self.mbc = "MBC5"
            self.ram = True
            self.battery = True
            self.rumble = True
        elif self.cartridge_type == 0xFC:
            self.mbc = "POCKET CAMERA"
        elif self.cartridge_type == 0xFD:
            self.mbc = "BANDAI TAMA5"
        elif self.cartridge_type == 0xFE:
            self.mbc = "HuC3"
        elif self.cartridge_type == 0xFF:
            self.mbc = "HuC1"
            self.ram = True
            self.battery = True
        else:
            print("Unknown cartridge type:", hex(self.cartridge_type))
            assert(False)
        assert(self.mbc != None)

    def ramInfo(self, rom):
        "Must be called after cartridgeType()"
        
        banks_code = rom[0x149]
        if banks_code == 1 or self.mbc == "MBC2":
            self.ram_banks = 1
        elif banks_code == 0:
            self.ram_banks = 0
        elif banks_code == 2:
            self.ram_banks = 1
        elif banks_code == 3:
            self.ram_banks = 4
        else:
            assert(False)

        if self.mbc == "MBC2":
            self.ram_size = 0x200
        elif banks_code == 0:
            self.ram_size = 0x0
        elif banks_code == 1:
            self.ram_size = 0x800
        elif banks_code == 2:
            self.ram_size = 0x2000
        elif banks_code == 3:
            self.ram_size = 0x8000
        else:
            assert(False)


    def romInfo(self, rom):
        banks_code = rom[0x148]

        if banks_code == 0x00:
            self.rom_banks = 1
        elif banks_code == 0x01:
            self.rom_banks = 4
        elif banks_code == 0x02:
            self.rom_banks = 8
        elif banks_code == 0x03:
            self.rom_banks = 16
        elif banks_code == 0x04:
            self.rom_banks = 32
        elif banks_code == 0x05:
            self.rom_banks = 64
        elif banks_code == 0x06:
            self.rom_banks = 128
        elif banks_code == 0x07:
            self.rom_banks = 128
        elif banks_code == 0x52:
            self.rom_banks = 72
        elif banks_code == 0x53:
            self.rom_banks = 80
        elif banks_code == 0x54:
            self.rom_banks = 96
        else:
            assert(False)

    def display(self):
        print("Title:", self.name)
        print("MBC:", self.mbc)
        print("RAM Banks:", self.ram_banks)
        print("ROM Banks:", self.rom_banks)
        print("ROM size:", str(self.rom_size // 1024) + "KB")
        print("Japanese:", self.japanese)
        print("RAM:", self.ram)
        print("Battery:", self.battery)
        print("Timer:", self.timer)
        print("Rumble:", self.rumble)
        print("****************************")
