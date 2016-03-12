import registers

class Emulator:
    def __init__(self, rom, header):
        self.rom    = rom
        self.ram    = [0 for i in range(0xFFFF)] # Quick hack
        self.header = header
        self.cycles = 0 # machine cycles
        self.opDesc = "" # Stores a human readable string of the current operation for debugging

        self.a      = registers.RegisterByte(0x0, 'A')
        self.f      = registers.RegisterByte(0x0, 'F')
        self.b      = registers.RegisterByte(0x0, 'B')
        self.c      = registers.RegisterByte(0x0, 'C')
        self.d      = registers.RegisterByte(0x0, 'D')
        self.e      = registers.RegisterByte(0x0, 'E')
        self.h      = registers.RegisterByte(0x0, 'H')
        self.l      = registers.RegisterByte(0x0, 'L')
        self.af     = registers.RegisterWord(self.a, self.f, 'AF')
        self.bc     = registers.RegisterWord(self.b, self.c, 'BC')
        self.de     = registers.RegisterWord(self.d, self.e, 'DE')
        self.hl     = registers.RegisterWord(self.h, self.l, 'HL')
        self.pc     = registers.RegisterWord.fromValue(0x100, 'PC')
        self.sp     = registers.RegisterWord.fromValue(0x0, 'SP')

        self.op_table = {

            0x00:         self.nop,
            
            # Loads
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
            
            0x36: lambda: self.ld_Xb(self.hl),
            0x02: lambda: self.ld_Xr(self.bc, self.a),
            0x12: lambda: self.ld_Xr(self.de, self.a),
            0x3A:         self.ldd_rX,
            0x32:         self.ldd_Xr,
            0x2A:         self.ldi_rX,
            0x22:         self.ldi_Xr,

            0x01: lambda: self.ld_xw(self.bc),
            0x11: lambda: self.ld_xw(self.de),
            0x21: lambda: self.ld_xw(self.hl),
            0x31: lambda: self.ld_xw(self.sp),
            0xF9: lambda: self.ld_xx(self.sp, self.hl),

            # Jumps
            0xC3:         self.jp_w,
            0xE9: lambda: self.jp_X(self.hl),

            # ALU
            0xAF: lambda: self.xor_r(self.a),
            0xA8: lambda: self.xor_r(self.b),
            0xA9: lambda: self.xor_r(self.c),
            0xAA: lambda: self.xor_r(self.d),
            0xAB: lambda: self.xor_r(self.e),
            0xAC: lambda: self.xor_r(self.h),
            0xAD: lambda: self.xor_r(self.l),
            0xAE: lambda: self.xor_X(self.hl),
            0xEE:         self.xor_b,
        }

    def run(self):
        print("\nPC: Operation")
        while True:
            
            self.opDesc = ""
            instruction = self.getMemory(int(self.pc))
            
            if instruction in self.op_table:
                self.op_table[instruction]()
            else:
                print("Instruction " + hex(instruction) + " not implemented! AAAAGH!! ... I'm dead ...")
                break

            if not self.opDesc:
                print("No opDesc for:", hex(instruction))

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
            print(hex(location))
            assert(False)
        else:
            self.ram[location - 0x4000] = value
    
    def setOpDesc(self, name, arg1="", arg2=""):
        self.opDesc = "{}: {}".format(hex(int(self.pc)), name)
        if arg1:
            self.opDesc += " " + arg1
        if arg2:
            self.opDesc += ", " + arg2
        print(self.opDesc)

    # To to keep the op_table aligned and for docuementation purposes
    # The following are used to refer to operands:
    #   r - register
    #   x - 16 bit register
    #   X - dereferenced 16 bit register
    #   b - byte (8 bit value)
    #   w - word (16 bit value)
    #   W - derefenced word
    #
    # They are not used to refer to the arguments that the functions
    # used to emulate the operation take instead they refer to the
    # operands required for that operation in Assembly.

    def nop(self):
        self.setOpDesc("NOP")
        self.pc += 1
        self.cycles += 1

    # Loads
    def ld_rr(self, r1, r2):
        self.setOpDesc("LD", r1.getName(), r2.getName())
        r1.set(int(r2))
        self.pc += 1
        self.cycles += 1

    def ld_rW(self, r):
        W = self.getOperationWord()
        self.setOpDesc("LD", r.getName(), "({})".format(asmHex(W)))
        r.set(self.getMemory(W))
        self.pc += 3
        self.cycles += 4

    def ld_rX(self, r, X):
        self.setOpDesc("LD", r.getName(), "({})".format(X.getName()))
        r.set(self.getMemory(int(X)))
        self.pc += 1
        self.cycles += 2

    def ld_rb(self, r):
        b = self.getOperationByte()
        self.setOpDesc("LD", r.getName(), asmHex(b))
        r.set(b)
        self.pc += 2
        self.cycles += 2

    def ld_Xb(self, X):
        b = self.getOperationByte()
        self.setOpDesc("LD", "({})".format(X.getName()), asmHex(b))
        self.setMemory(int(X), b)
        self.pc += 2
        self.cycles += 3

    def ld_Xr(self, X, r):
        self.setOpDesc("LD",  "({})".format(X.getName()), r.getName())
        self.setMemory(int(X), int(r))
        self.pc += 1
        self.cycles += 2

    def ld_xw(self, x):
        w = self.getOperationWord()
        self.setOpDesc("LD", x.getName(), asmHex(w))
        x.set(w)
        self.pc += 3
        self.cycles += 3

    def ld_xx(self, x1, x2):
        self.setOpDesc("LD", x1.getName(), x2.getName())
        x1.set(int(x2))
        self.pc += 1
        self.cycles += 2

    def ld_Wr(self, r): #Currently unused?
        W = self.getOperationWord()
        self.setOpDesc("LD", "({})".format(asmHex(W)), r.getName())
        self.setMemory(W, int(r))
        self.pc += 3
        self.cycles += 4

    def ldd_rX(self):
        self.setOpDesc("LDD", "A", "({HL})")
        self.a.set(self.getMemory(int(self.hl)))
        self.hl -= 1
        self.pc += 1
        self.cycles += 2

    def ldd_Xr(self):
        self.setOpDesc("LDD", "({HL})", "A")
        self.setMemory(int(self.hl), int(self.a))
        self.hl -= 1
        self.pc += 1
        self.cycles += 2

    def ldi_rX(self):
        self.setOpDesc("LDI", "A", "({HL})")
        self.a.set(self.getMemory(int(self.hl)))
        self.hl += 1
        self.pc += 1
        self.cycles += 2

    def ldi_Xr(self):
        self.setOpDesc("LDI", "({HL})", "A")
        self.setMemory(int(self.hl), int(self.a))
        self.hl += 1
        self.pc += 1
        self.cycles += 2

    # Jumps
    def jp_w(self):
        w = self.getOperationWord()
        self.setOpDesc("JP", format(asmHex(w)))
        self.pc.set(w)
        self.cycles += 3

    def jp_X(self, X):
        self.setOpDesc("JP", X.getName())
        self.pc.set(self.getMemory(int(x)))
        self.cycles += 1

    # ALU
    def xor_r(self, r):
        self.setOpDesc("XOR", r.getName())
        xor = int(self.a) ^ int(r)
        self.a.set(xor)
        self.pc += 1
        self.cycles += 1

    def xor_X(self, X):
        self.setOpDesc("XOR", "({})".format(X.getName()))
        xor = int(self.a) ^ self.getMemory(int(X))
        self.a.set(xor)
        self.pc += 1
        self.cycles += 2

    def xor_b(self):
        b = self.getOperationByte()
        self.setOpDesc("XOR", asmHex(b))
        xor = int(self.a) ^ b
        self.a.set(xor)
        self.pc += 2
        self.cycles += 2

if __name__ == '__main__':
    import doctest
    doctest.testmod()

# Chuck this in another file
def asmHex(integer):
    return '$' + hex(integer)[2:]
