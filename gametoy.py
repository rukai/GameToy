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

        mem = Memory(rom)
        print("\nPC:    Operation")
        
        interrupts = Interrupts(mem)
        cpu = CPU(mem, interrupts)
        lcdc = LCDC(mem)
        while cpu.running:
            interrupts.update()
            cpu.run()
            lcdc.update()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        run(sys.argv[1])
    else:
        print("Usage: gametoy rompath")
