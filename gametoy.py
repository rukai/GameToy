#!/bin/env python3

import sys
import os
from cpu import CPU
from memory import Memory
from interrupts import Interrupts
from lcdc import LCDC
from header import Header

help = """
Usage: gametoy rompath [debug mode] [max cycles]

[debug modes]: display debug info
    values: NONE, INSTRUCTIONS, REGISTERS, HEADER, TITLE, ALL
[max cycles]: emulates this many cycles before exiting
    values: integer >= 0
"""

def run(path, debug, max_cycles):
    with open(path, "rb") as rom_file:
        debug_title = debug == "TITLE"
        debug_header = debug == "HEADER" or debug == "ALL"
        debug_mem = debug == "MEM" or debug == "ALL"
        debug_instructions = debug == "INSTRUCTIONS" or debug == "ALL"
        debug_registers = debug == "REGISTERS" or debug == "ALL"
        rom = [i for i in rom_file.read()]
        
        
        header = Header(rom, debug_header)
        mem = Memory(rom, header)
        if debug_title:
            print("Title: " + header.name)
        if debug_instructions:
            print("PC:    Operation")
        
        interrupts = Interrupts()
        cpu = CPU(mem, interrupts, debug_instructions, debug_registers)
        lcdc = LCDC(mem, interrupts)
        mem.setupIO(lcdc, interrupts)
        while cpu.run_state != "QUIT":
            interrupts.update()
            if cpu.run_state == "RUN":
                cpu.run()
            else:
                cpu.cycles += 1
            lcdc.update()

            if max_cycles >= 0 and cpu.cycles > max_cycles:
                cpu.run_state = "QUIT"

def main():
    if len(sys.argv) > 1:
        path = os.path.abspath(sys.argv[1])

        if len(sys.argv) > 2:
            debug = sys.argv[2]

            if len(sys.argv) > 3:
                max_cycles = int(sys.argv[3])
                run(path, debug, max_cycles)
            else:
                run(path, debug, -1)
        else:
            run(path, "NONE", -1)
    else:
        print(help)

if __name__ == "__main__":
    main()
