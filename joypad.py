import pygame

class Joypad:
    def __init__(self):
        self.disable_buttons    = True
        self.disable_directions = True

        self.start  = 1
        self.select = 1
        self.b      = 1
        self.a      = 1
        self.down   = 1
        self.up     = 1
        self.left   = 1
        self.right  = 1

    def keyEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.down = 0
            if event.key == pygame.K_UP:
                self.up = 0
            if event.key == pygame.K_LEFT:
                self.left = 0
            if event.key == pygame.K_RIGHT:
                self.right = 0
            if event.key == pygame.K_a:
                self.start = 0
            if event.key == pygame.K_s:
                self.select = 0
            if event.key == pygame.K_x:
                self.b = 0
            if event.key == pygame.K_z:
                self.a = 0

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                self.down = 1
            if event.key == pygame.K_UP:
                self.up = 1
            if event.key == pygame.K_LEFT:
                self.left = 1
            if event.key == pygame.K_RIGHT:
                self.right = 1
            if event.key == pygame.K_a:
                self.start = 1
            if event.key == pygame.K_s:
                self.select = 1
            if event.key == pygame.K_x:
                self.b = 1
            if event.key == pygame.K_z:
                self.a = 1

    def readJOYP(self):
        value =  int(self.disable_buttons)    << 5
        value |= int(self.disable_directions) << 4

        if not self.disable_directions:
            value |= self.down << 3
            value |= self.up   << 2
            value |= self.left << 1
            value |= self.right

        if not self.disable_buttons:
            value |= self.start  << 3
            value |= self.select << 2
            value |= self.b      << 1
            value |= self.a
    
        return value
    
    def writeJOYP(self, value):
        self.disable_buttons    = bool(value & 0b00100000)
        self.disable_directions = bool(value & 0b00010000)
