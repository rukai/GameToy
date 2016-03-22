class Interrupts:
    def __init__(self):
        self.ime_counter = 0
            
        self.ime = True
        self.ime_new = True
        self.iflag = 0
        self.ie = 0
        self.locations = [
            0x0040, #V-Blank
            0x0048, #LCDC
            0x0050, #Timer
            0x0058, #Serial
            0x0060  #Joypad
        ]

    def setIFbit(self, bit):
        self.iflag |= (1 << bit)

    def clearIFbit(self, bit):
        self.iflag &= (~(1 << bit))

    def setCall(self, call):
        self.call = call

    def setIME(self, enable):
        self.ime_counter = 2
        self.ime_new = enable

    def update(self):
        if self.ime_counter > 0:
            self.ime_counter -= 1

        if self.ime_counter == 0:
            self.ime = self.ime_new
        
        if self.ime:
            check = self.ie & self.iflag

            for i, location in enumerate(self.locations):
                if check & (1 << i):
                    self.ime = False
                    self.clearIFbit(i)
                    self.call(location)
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

    def readIF(self):
        return self.iflag

    def writeIF(self, value):
        self.iflag = value

    def readIE(self):
        return self.ie

    def writeIE(self, value):
        self.ie = value
