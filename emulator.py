class Emulator:
    def __init__(self, rom, header):
        self.rom    = rom
        self.ram    = [0 for i in range(0xFFFF)] # Quick hack
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
        self.hl     = RegisterWord(self.h, self.l)
        self.pc     = RegisterWord.fromValue(0x100)
        self.sp     = RegisterWord.fromValue(0x0)

        self.op_table = {
            0x00: self.nop,
            
            0x7F: lambda: self.ld_rr(self.a, self.a),
            0x78: lambda: self.ld_rr(self.a, self.b),
            0x79: lambda: self.ld_rr(self.a, self.c),
            0x7A: lambda: self.ld_rr(self.a, self.d),
            0x7B: lambda: self.ld_rr(self.a, self.e),
            0x7C: lambda: self.ld_rr(self.a, self.h),
            0x7D: lambda: self.ld_rr(self.a, self.l),
            0x7E: lambda: self.ld_rX(self.a, self.hl),
            0x0A: lambda: self.ld_rX(self.a, self.bc),
            0x1A: lambda: self.ld_rX(self.a, self.de),
            0x3A: lambda: self.ld_rW(self.a),

            0x47: lambda: self.ld_rr(self.b, self.a),
            0x40: lambda: self.ld_rr(self.b, self.b),
            0x41: lambda: self.ld_rr(self.b, self.c),
            0x42: lambda: self.ld_rr(self.b, self.d),
            0x43: lambda: self.ld_rr(self.b, self.e),
            0x44: lambda: self.ld_rr(self.b, self.h),
            0x45: lambda: self.ld_rr(self.b, self.l),
            0x46: lambda: self.ld_rX(self.b, self.hl),

            0x4F: lambda: self.ld_rr(self.c, self.a),
            0x48: lambda: self.ld_rr(self.c, self.b),
            0x49: lambda: self.ld_rr(self.c, self.c),
            0x4A: lambda: self.ld_rr(self.c, self.d),
            0x4B: lambda: self.ld_rr(self.c, self.e),
            0x4C: lambda: self.ld_rr(self.c, self.h),
            0x4D: lambda: self.ld_rr(self.c, self.l),
            0x4E: lambda: self.ld_rX(self.c, self.hl),

            0x57: lambda: self.ld_rr(self.d, self.a),
            0x50: lambda: self.ld_rr(self.d, self.b),
            0x51: lambda: self.ld_rr(self.d, self.c),
            0x52: lambda: self.ld_rr(self.d, self.d),
            0x53: lambda: self.ld_rr(self.d, self.e),
            0x54: lambda: self.ld_rr(self.d, self.h),
            0x55: lambda: self.ld_rr(self.d, self.l),
            0x56: lambda: self.ld_rX(self.d, self.hl),

            0x5F: lambda: self.ld_rr(self.e, self.a),
            0x58: lambda: self.ld_rr(self.e, self.b),
            0x59: lambda: self.ld_rr(self.e, self.c),
            0x5A: lambda: self.ld_rr(self.e, self.d),
            0x5B: lambda: self.ld_rr(self.e, self.e),
            0x5C: lambda: self.ld_rr(self.e, self.h),
            0x5D: lambda: self.ld_rr(self.e, self.l),
            0x5E: lambda: self.ld_rX(self.e, self.hl),

            0x67: lambda: self.ld_rr(self.h, self.a),
            0x60: lambda: self.ld_rr(self.h, self.b),
            0x61: lambda: self.ld_rr(self.h, self.c),
            0x62: lambda: self.ld_rr(self.h, self.d),
            0x63: lambda: self.ld_rr(self.h, self.e),
            0x64: lambda: self.ld_rr(self.h, self.h),
            0x65: lambda: self.ld_rr(self.h, self.l),
            0x66: lambda: self.ld_rX(self.h, self.hl),

            0x6F: lambda: self.ld_rr(self.l, self.a),
            0x68: lambda: self.ld_rr(self.l, self.b),
            0x69: lambda: self.ld_rr(self.l, self.c),
            0x6A: lambda: self.ld_rr(self.l, self.d),
            0x6B: lambda: self.ld_rr(self.l, self.e),
            0x6C: lambda: self.ld_rr(self.l, self.h),
            0x6D: lambda: self.ld_rr(self.l, self.l),
            0x6E: lambda: self.ld_rX(self.l, self.hl),

            0x77: lambda: self.ld_Xr(self.hl, self.a),
            0x70: lambda: self.ld_Xr(self.hl, self.b),
            0x71: lambda: self.ld_Xr(self.hl, self.c),
            0x72: lambda: self.ld_Xr(self.hl, self.d),
            0x73: lambda: self.ld_Xr(self.hl, self.e),
            0x74: lambda: self.ld_Xr(self.hl, self.h),
            0x75: lambda: self.ld_Xr(self.hl, self.l),

            0x3E: lambda: self.ld_rb(self.a),
            0x06: lambda: self.ld_rb(self.b),
            0x0E: lambda: self.ld_rb(self.c),
            0x16: lambda: self.ld_rb(self.d),
            0x1E: lambda: self.ld_rb(self.e),
            0x26: lambda: self.ld_rb(self.h),
            0x2E: lambda: self.ld_rb(self.l),

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

    def getOperationByte(self):
        value = self.getMemory(int(self.pc)+1)
        assert(value <= 0xFF)
        return value

    def getMemory(self, location):
        if location < 0x4000:
            return self.rom[location]
        else:
            return self.ram[location - 0x4000]

    def setMemory(self, location, value):
        if location < 0x4000:
            assert(False)
        else:
            self.ram[location - 0x4000] = value

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
        #self.clocks += TODO

    def ld_rX(self, r, X):
        r.set(self.getMemory(int(X)))
        self.pc += 1
        #self.clocks += TODO

    def ld_rb(self, r):
        r.set(self.getOperationByte())
        self.pc += 2
        #self.clocks += TODO

    def ld_Xr(self, X, r):
        self.setMemory(int(X), int(r))
        self.pc += 1
        #self.clocks += TODO

    def ld_xw(self, x):
        x.set(self.getOperationWord())
        self.pc += 3
        #self.clocks += TODO

    def jp(self, w):
        self.pc.set(w)
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
