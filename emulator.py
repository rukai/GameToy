def run(rom):
    run = True
    pc = 0x100
    while run:
        instruction = rom[pc]
        print(hex(pc), hex(instruction))
    
        if instruction == 0x00: #NOP
            pc += 1
        elif instruction == 0xC3: #JP nn
            pc = rom[pc+1] + rom[pc+2] << 8
        elif instruction == 0x4D: #LD C L
            pc += 3
        else:
            print("Instruction not implemented! AAAAGH!!")
            run = False
