#!/bin/env python3

import sys
import os
import emulator

def run(path):
    path = os.path.abspath(path)
    with open(path, 'rb') as romFile:
        rom = [i for i in romFile.read() ]

        header = Header(rom)
        print(header.name)
        emulator.run(rom)

class Header:
    def __init__(self, rom):
        self.cartridgeType = rom[0x147]
        self.romSize = rom[0x138]

        self.name = ""
        for byte in rom[0x134:0x149]:
            if byte != 0:
                self.name += chr(byte)

        self.japanese = True
        if(rom[0x14A] == 1):
            self.japanese = False

if __name__ == "__main__":
    run(sys.argv[1])
