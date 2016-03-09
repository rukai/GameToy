class Emulator:
    def __init__(self, rom, header):
        self.rom    = rom
        self.header = header
        self.clocks = 0

        self.a      = RegisterByte(0x0)
        self.f      = RegisterByte(0x0)
        self.b      = RegisterByte(0x0)
        self.c      = RegisterByte(0x0)
        self.d      = RegisterByte(0x0)
        self.e      = RegisterByte(0x0)
        self.h      = RegisterByte(0x0)
        self.l      = RegisterByte(0x0)
        self.af     = RegisterWord(self.a, self.f)
        self.bc     = RegisterWord(self.b, self.c)
        self.de     = RegisterWord(self.d, self.e)
        self.pc     = RegisterWord.fromValue(0x100)
        self.sp     = RegisterWord.fromValue(0x0)

        self.op_table = {
            0x00: lambda: self.nop(),
            
            0x7F: lambda: self.ld_rr(self.a, self.a),
            0x78: lambda: self.ld_rr(self.a, self.b),
            0x79: lambda: self.ld_rr(self.a, self.c),
            0x7A: lambda: self.ld_rr(self.a, self.d),
            0x7B: lambda: self.ld_rr(self.a, self.e),
            0x7C: lambda: self.ld_rr(self.a, self.h),
            0x7D: lambda: self.ld_rr(self.a, self.l),
            0x7E: lambda: self.ld_rX(self.a, self.hl()),
            0x0A: lambda: self.ld_rX(self.a, self.bc()),
            0x1A: lambda: self.ld_rX(self.a, self.de()),
            0x3A: lambda: self.ld_rW(self.a, self.getOperationWord()),

            0x47: lambda: self.ld_rr(self.b, self.a),
            0x40: lambda: self.ld_rr(self.b, self.b),
            0x41: lambda: self.ld_rr(self.b, self.c),
            0x42: lambda: self.ld_rr(self.b, self.d),
            0x43: lambda: self.ld_rr(self.b, self.e),
            0x44: lambda: self.ld_rr(self.b, self.h),
            0x45: lambda: self.ld_rr(self.b, self.l),
            0x46: lambda: self.ld_rW(self.b, self.getOperationWord()),

            0x4F: lambda: self.ld_rr(self.c, self.a),
            0x48: lambda: self.ld_rr(self.c, self.b),
            0x49: lambda: self.ld_rr(self.c, self.c),
            0x4A: lambda: self.ld_rr(self.c, self.d),
            0x4B: lambda: self.ld_rr(self.c, self.e),
            0x4C: lambda: self.ld_rr(self.c, self.h),
            0x4D: lambda: self.ld_rr(self.c, self.l),
            0x4E: lambda: self.ld_rW(self.c),

            0x01: lambda: self.ld_xw(self.bc),

            0xC3: lambda: self.jp(self.getOperationWord())
        }

    def run(self):
        loop = True
        while loop:
            instruction = self.getMemory(int(self.pc))
            print(hex(int(self.pc)), hex(instruction))
        
            if instruction in self.op_table:
                self.op_table[instruction]()
            else:
                print("Instruction not implemented! AAAAGH!! ... I'm dead ...")
                loop = False

    def getOperationWord(self):
        value = self.getMemory(int(self.pc)+1) + (self.getMemory(int(self.pc)+2) << 8)
        assert(value <= 0xFFFF)
        return value

    def getMemory(self, i):
        return self.rom[i] #TODO

    # Op codes operand key:
    #   r - register
    #   x - 16 bit register
    #   X - dereferenced 16 bit register
    #   b - byte (8 bit value)
    #   w - word (16 bit value)
    #   W - derefenced word
    # These are used to keep the op_table clean and aligned

    def nop(self):
        self.pc += 1
        self.clocks += 1

    def ld_rr(self, r1, r2):
        r1.set(int(r2))
        self.pc += 1
        self.clocks += 4

    def ld_rW(self, r):
        r.set(self.getMemory(self.getOperationWord()))
        self.pc += 3
        #self.clocks = TODO

    def ld_xw(self, r):
        r.set(self.getOperationWord())
        self.pc += 3
        #self.clocks = TODO

    def jp(self, nn):
        self.pc.set(nn)
        self.clocks += 16

class RegisterByte:
    def __init__(self, value):
        assert(value <= 0xFF)
        self.value = int(value)

    def set(self, value):
        assert(value <= 0xFF)
        self.value = int(value)

    def __add__(self, value):
        if type(value) == RegisterByte:
            return RegisterByte(self.value + int(value))
        return self.value + value

    def __iadd__(self, value):
        self.value += value
        assert(value <= 0xFF)
        return self

    def __eq__(self, value):
        return self.value == value

    def __int__(self):
        return self.value
    
    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return 'RegisterByte(' + hex(self.value) + ')'

class RegisterWord:
    def __init__(self, r1, r2):
        self.r1 = r1 # Most significant
        self.r2 = r2 # Least significant

    @classmethod
    def fromValue(cls, value):
        """
        >>> RegisterWord.fromValue(0x0)
        RegisterWord(0x0)
        >>> RegisterWord.fromValue(0xf)
        RegisterWord(0xf)
        >>> RegisterWord.fromValue(0xf).r2
        RegisterByte(0xf)
        >>> RegisterWord.fromValue(0xff)
        RegisterWord(0xff)
        >>> RegisterWord.fromValue(0x100)
        RegisterWord(0x100)
        >>> print(RegisterWord.fromValue(555))
        555
        """
        register = cls(RegisterByte(0), RegisterByte(0))
        register.set(value)
        return register

    def set(self, value):
        self.r1.set(value >> 8)
        self.r2.set(value & 0x00FF)

    def __add__(self, value):
        if type(value) == RegisterWord:
            return RegisterWord(int(self) + int(value))
        return int(self) + value

    def __iadd__(self, value):
        self.set(int(self) + value)
        return self

    def __int__(self):
        return (int(self.r1) << 8) + int(self.r2)

    def __eq__(self, value):
        return int(self) == value
    
    def __str__(self):
        return str(int(self))

    def __repr__(self):
        return 'RegisterWord(' + hex(int(self)) + ')'

if __name__ == '__main__':
    import doctest
    doctest.testmod()
