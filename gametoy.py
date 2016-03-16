#!/bin/env python3

import sys
import os
from cpu import CPU
from memory import Memory
from interrupts import Interrupts
from lcdc import LCDC

def run(path):
    path = os.path.abspath(path)
    with open(path, "rb") as rom_file:
        rom = [i for i in rom_file.read() ]

        header = Header(rom)
        print(header.name)
        print("\nPC:    Operation")
        
        mem = Memory(rom, header)
        interrupts = Interrupts(mem)
        cpu = CPU(mem, interrupts)
        lcdc = LCDC(mem)
        while cpu.running:
            interrupts.update()
            cpu.run()
            lcdc.update()

class Header:
    def __init__(self, rom):
        self.cartridge_type = rom[0x147]
        self.rom_size = rom[0x138]

        self.name = ""
        for byte in rom[0x134:0x149]:
            if byte != 0:
                self.name += chr(byte)

        self.japanese = True
        if(rom[0x14A] == 1):
            self.japanese = False

if __name__ == "__main__":
    if len(sys.argv) == 2:
        run(sys.argv[1])
    else:
        print("Usage: gametoy rompath")
