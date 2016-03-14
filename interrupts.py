class Interrupts:
    def __init__(self, memory):
        self.counter = 0
        self.enable_new = True
        self.enable = True
        self.mem = memory
        self.locations = [
            0x0040, #V-Blank
            0x0048, #LCDC
            0x0050, #Timer
            0x0058, #Serial
            0x0060  #Joypad
        ]

    def setIFbit(self, bit):
        value = self.mem.get(0xFF0F)
        self.mem.set(0xFF0F, value | (1 << bit))

    def clearIFbit(self, bit):
        value = self.mem.get(0xFF0F)
        self.mem.set(0xFF0F, value & (~(1 << bit)))

    def setCall(self, call):
        self.call = call

    def setEnable(self, enable):
        self.enable_counter = 2
        self.enable_new = enable

    def update(self):
        if self.counter > 0:
            self.counter -= 1

        if self.counter == 0:
            self.enable = self.enable_new
        
        if self.enable:
            ie = self.mem.get(0xFFFF)
            iflag = self.mem.get(0xFF0F)
            check = ie & iflag

            for i, location in enumerate(self.locations):
                if check & (1 << i):
                    self.enable = False
                    self.clearIFbit(i)
                    self.callBase(location)
                    return
        
    def callVBlank(self):
        self.setIFbit(0)

    def callLCDC(self):
        self.setIFbit(1)

    def callTimer(self):
        self.setIFbit(2)

    def callSerial(self):
        self.setIFbit(3)

    def callJoypadToggle(self):
        self.setIFbit(4)
