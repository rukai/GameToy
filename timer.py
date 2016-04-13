class Timer:
    def __init__(self, interrupts):
        self.interrupts = interrupts
        self.div          = 0 # FF04
        self.sub_div      = 0
        self.tima         = 0 # FF05
        self.sub_tima     = 0
        self.tma          = 0 # FF06

        # FF07 bits 2-0
        self.timer_run   = False
        self.clock_select = 0

        self.clock        = 0

    def update(self, cycles):
        self.sub_div += cycles
        if self.sub_div >= 256:
            self.div = (self.div + 1) % 0x100

        if self.timer_run:
            self.sub_tima += cycles
        else:
            self.sub_tima = 0 # Assuming timer progress is lost when disabled
        if self.sub_tima >= self.clock:
            if self.tima == 0xFF:
                self.tima = self.tma
                self.interrupts.callTimer()
            else:
                self.tima += 1

    # Divider Register
    def readDIV(self):
        return self.div

    def writeDIV(self, value):
        self.div = 0

    # Timer Counter
    def readTIMA(self):
        return self.tima

    def writeTIMA(self, value):
        self.tima = value

    # Timer Modulo
    def readTMA(self):
        return self.tma

    def writeTMA(self, value):
        self.tma = value

    # Timer Controller
    def readTAC(self):
        value = int(timer_run) << 2
        value |= clock_select
        return value

    def writeTAC(self, value):
        self.timer_run = bool(value & 0b00000100)
        self.clock_select =    value & 0b00000011
        
        if self.clock_select == 0:
            self.clock = 1024
        elif self.clock_select == 1:
            self.clock = 16
        elif self.clock_select == 2:
            self.clock = 64
        elif self.clock_select == 3:
            self.clock = 256
        else:
            assert(False)
