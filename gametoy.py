#!/bin/env python3

import sys
import os
import emulator

def run(path):
    path = os.path.abspath(path)
    with open(path, 'rb') as rom_file:
        rom = [i for i in rom_file.read() ]

        header = Header(rom)
        print(header.name)
        emu = emulator.Emulator(rom, header)
        emu.run()

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
