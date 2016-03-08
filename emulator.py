def run(rom):
    run = True
    af = Register(0x0)
    bc = Register(0x0)
    de = Register(0x0)
    hl = Register(0x0)
    pc = Register(0x100)
    sp = Register(0x0)
    while run:
        instruction = rom[int(pc)]
        print(hex(int(pc)), hex(instruction))
    
        if instruction == 0x00: #NOP
            pc += 1
        elif instruction == 0xC3: #JP nn
            pc = Register(rom[pc+1] + rom[pc+2] << 8)
        elif instruction == 0x4D: #LD C L
            pc += 3
        else:
            print("Instruction not implemented! AAAAGH!! ... I'm dead ...")
            run = False

# Represents 16 bit register accessible as individual bytes
class Register:
    def __init__(self, value):
        self.value = int(value) % 65536 #does it even loop? signed/unsigned?

    def __add__(self, value):
        if type(value) == Register:
            return Register(self.value + value)
        return self.value + value

    def __iadd__(self, value):
        self.value += value
        return self

    def __eq__(self, value):
        return self.value == value

    def __int__(self):
        return self.value
    
    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return 'Register(' + str(self.value) + ')'

    def setMSB():
        pass
    def setLSB():
        pass
    def getMSB():
        pass
    def getLSB():
        pass
