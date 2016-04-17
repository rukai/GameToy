import pygame

class LCDC:
    def __init__(self, mem, interrupts):
        self.mem = mem
        self.interrupts = interrupts

        # FF40 bits 7-0
        # w - window
        # bg - background
        self.display_enable             = False
        self.w_tile_map_select          = False
        self.w_display_enable           = False
        self.bg_w_tile_data_select      = False
        self.bg_tile_map_select         = False
        self.sprite_size                = False
        self.sprite_display_enable      = False
        self.bg_display_enable          = False

        # FF41 bits 6-0
        self.enable_lyc_interrupt    = False
        self.enable_oam_interrupt    = False
        self.enable_vblank_interrupt = False
        self.enable_hblank_interrupt = False
        self.mode                    = 2 # bits 1-0
        self.mode_counter            = 0 
        # self.mode possible states:
        # 0 - H-Blank
        # 1 - V-Blank
        # 2 - Searching OAM-RAM
        # 3 - Transferring data to LCD Driver
        # Transitions: 2 -> 3 -> 0 -> (2 or 1 -> 2)
        
        self.scy = 0 #FF42
        self.scx = 0 #FF43
        self.ly  = 0 #FF44
        self.lyc = 0 #FF45
        self.wy  = 0 #FF4A
        self.wx  = 0 #FF4B

        # FF47 bits 7-0
        # self.bgp_colorx possible states:
        # 0 - white
        # 1 - light gray
        # 2 - dark gray
        # 3 - black
        self.bgp_color0 = 0
        self.bgp_color1 = 0
        self.bgp_color2 = 0
        self.bgp_color3 = 0

        # FF48 bits
        # color0 is unused because sprites render it as transparent
        self.obp0_color1 = 0
        self.obp0_color2 = 0
        self.obp0_color3 = 0

        # FF49 bits
        self.obp1_color1 = 0
        self.obp1_color2 = 0
        self.obp1_color3 = 0
    
        self.tiles = {}
        self.screen = pygame.Surface((160, 144), pygame.SRCALPHA)
        self.display = pygame.display.set_mode((160 * 4, 144 * 4))
        pygame.display.set_caption("GAMETOY")
        self.emu_palette = [
            [224, 248, 208],
            [136, 192, 112],
            [ 48, 104,  80],
            [  8,  24,  32],
        ]

    def render(self):
        self.tiles = {}
        if self.display_enable:
            self.screen.fill((255, 0, 255)) # self.screen.fill(self.emu_palette[0])
            if self.bg_display_enable:
                self.renderBG()
                self.tiles = {}
            if self.w_display_enable:
                self.renderW()
                self.tiles = {}
            if self.sprite_display_enable:
                self.renderSprites()
                self.tiles = {}
        else:
            self.screen.fill((255, 0, 0)) # TODO: remove debug color
        upscaled = pygame.transform.scale(self.screen, (self.screen.get_width() * 4, self.screen.get_height() * 4),)
        self.display.blit(upscaled, (0, 0))
        pygame.display.flip()

    def renderSprites(self):
        for i in range(40):
            address = 0xFE00 + i * 4
            y_pos      = self.mem.read(address)     - 16
            x_pos      = self.mem.read(address + 1) - 8
            tile_index = self.mem.read(address + 2)
            flags      = self.mem.read(address + 3)

            below_BG = bool(flags & 0b10000000)
            y_flip   = bool(flags & 0b01000000)
            x_flip   = bool(flags & 0b00100000)
            palette  = bool(flags & 0b00010000)

            getColor = self.getOBP1Color if palette else self.getOBP0Color

            if self.sprite_size: # 8x16
                tile0_address = 0x8000 + (tile_index & 0b11111110) * 16
                tile1_address = 0x8000 + (tile_index | 0b00000001) * 16

                tile0 = self.renderTile(tile0_address, getColor)
                tile1 = self.renderTile(tile1_address, getColor)
                tile0 = pygame.transform.flip(tile0, x_flip, y_flip)
                tile1 = pygame.transform.flip(tile1, x_flip, y_flip)
                self.blitSprite(tile0, x_pos, y_pos, below_BG)
                self.blitSprite(tile1, x_pos, y_pos+8, below_BG)

            else: # 8x8
                tile_address = 0x8000 + tile_index * 16

                tile = self.renderTile(tile_address, getColor)
                tile = pygame.transform.flip(tile, x_flip, y_flip)
                self.blitSprite(tile, x_pos, y_pos, below_BG)

    def blitSprite(self, tile, sprite_x, sprite_y, below_BG):
        if below_BG and self.bg_display_enable:
            for x in range(8):
                for y in range(8):
                    screen_location = (sprite_x + x, sprite_y + y)
                    if screen_location[0] >= 160:
                        return
                    if screen_location[1] >= 144:
                        break;
                    if screen_location[0] <= 0 or screen_location[1] <= 0:
                        continue;

                    print(screen_location)
                    if self.screen.get_at(screen_location) == 0:
                        color = tile.get_at(x, y)
                        self.screen.set_at(screen_location, color)
        else:
            self.screen.blit(tile, (sprite_x, sprite_y))

    def renderBG(self):
        if self.bg_tile_map_select:
            start_address = 0x9C00
        else:
            start_address = 0x9800

        if self.bg_w_tile_data_select:
            tile_start_address = 0x8000
            read = self.mem.read
        else:
            tile_start_address = 0x9000
            read = self.mem.readSigned

        for y in range(19):
            for x in range(21):
                x_address = (x-1) + self.scx // 8
                y_address = ((y-1) + self.scy // 8) * 32
                address = start_address + (x_address + y_address) % 1024
                tile_address = tile_start_address + read(address) * 16
                tile = self.renderTile(tile_address, self.getBGColor)
                x_pos = (x-1) * 8 + (self.scx % 8)
                y_pos = (y-1) * 8 + (self.scy % 8)
                self.screen.blit(tile, (x_pos, y_pos))

    def renderW(self):
        if self.w_tile_map_select:
            start_address = 0x9C00
        else:
            start_address = 0x9800

        if self.bg_w_tile_data_select:
            tile_start_address = 0x8000
            read = self.mem.read
        else:
            tile_start_address = 0x8800
            read = self.mem.readSigned

        for y in range(18):
            for x in range(20):
                x_address = x + self.scx // 8
                y_address = (y + self.scy // 8) * 32
                address = start_address + (x_address + y_address) % 1024
                tile_address = tile_start_address + read(address) * 16
                tile = self.renderTile(tile_address, self.getBGColor)
                x_pos = x * 8 + self.wx - 7
                y_pos = y * 8 + self.wy
                self.screen.blit(tile, (x_pos, y_pos))

    def renderTile(self, address, getColor):
        if address in self.tiles:
            return self.tiles[address]

        tile = pygame.Surface((8, 8), pygame.SRCALPHA)
        for y in range(8):
            address_y = address + y * 2
            low_byte  = self.mem.read(address_y)
            high_byte = self.mem.read(address_y + 1)
            for x in range(8):
                mask = 1 << x
                low_bit = int(bool(low_byte & mask))
                high_bit = int(bool(high_byte & mask))
                color = (high_bit << 1) | low_bit
                tile.set_at((7 - x, y), getColor(color))
                self.tiles[address] = tile
        return tile

    def getBGColor(self, color):
        if color == 0:
            return self.emu_palette[self.bgp_color0]
        elif color == 1:
            return self.emu_palette[self.bgp_color1]
        elif color == 2:
            return self.emu_palette[self.bgp_color2]
        elif color == 3:
            return self.emu_palette[self.bgp_color3]

    def getOBP0Color(self, color):
        if color == 0:
            return (0, 0, 0, 0)
        elif color == 1:
            return self.emu_palette[self.obp0_color1]
        elif color == 2:
            return self.emu_palette[self.obp0_color2]
        elif color == 3:
            return self.emu_palette[self.obp0_color3]

    def getOBP1Color(self, color):
        if color == 0:
            return (0, 0, 0, 0)
        elif color == 1:
            return self.emu_palette[self.obp1_color1]
        elif color == 2:
            return self.emu_palette[self.obp1_color2]
        elif color == 3:
            return self.emu_palette[self.obp1_color3]

    def update(self, cycles):
        self.mode_counter += cycles
        if self.mode == 0:
            if self.mode_counter >= 204:
                self.mode_counter = 0
                self.ly += 1
                if self.ly == 144: # Reached end of screen
                    self.updateInterrupts(1)
                else:
                    self.updateInterrupts(2)
        elif self.mode == 1:
            if self.mode_counter >= 4560:
                self.mode_counter = 0
                self.mode = 2
                self.updateInterrupts(2)
                self.ly = 0
            if self.mode_counter % 456 == 0 and self.mode_counter != 0:
                self.ly += 1
        elif self.mode == 2:
            if self.mode_counter >= 80:
                self.mode_counter = 0
                self.updateInterrupts(3)
        elif self.mode == 3:
            if self.mode_counter >= 172:
                self.mode_counter = 0
                self.updateInterrupts(0)
                self.render()
        else:
            assert(False)

    def updateInterrupts(self, mode):
        self.mode = mode

        if self.mode == 1:
            self.interrupts.callVBlank()
            return

        lyc_interrupt = (self.ly == self.lyc) and self.enable_lyc_interrupt
        oam_interrupt = self.mode == 2 and self.enable_oam_interrupt
        hblank_interrupt = self.mode == 0 and self.enable_hblank_interrupt
        stat_vblank_interrupt = self.mode == 1 and self.enable_vblank_interrupt

        if lyc_interrupt or lyc_interrupt or oam_interrupt or hblank_interrupt or stat_vblank_interrupt:
            self.interrupts.callLCDC()
            return

    # LCD Control
    def readLCDC(self):
        value =  int(self.display_enable)             << 7
        value |= int(self.w_tile_map_select)          << 6
        value |= int(self.w_display_enable)           << 5
        value |= int(self.bg_w_tile_data_select)      << 4
        value |= int(self.bg_tile_map_select)         << 3
        value |= int(self.sprite_size)                << 2
        value |= int(self.sprite_display_enable)      << 1
        value |= int(self.bg_display_enable)          << 0
        return value

    def writeLCDC(self, value):
        self.display_enable             = bool(value & 0b10000000)
        self.w_tile_map_select          = bool(value & 0b01000000)
        self.w_display_enable           = bool(value & 0b00100000)
        self.bg_w_tile_data_select      = bool(value & 0b00010000)
        self.bg_tile_map_select         = bool(value & 0b00001000)
        self.sprite_size                = bool(value & 0b00000100)
        self.sprite_display_enable      = bool(value & 0b00000010)
        self.bg_display_enable          = bool(value & 0b00000001)

    # LCD Status
    def readSTAT(self):
        value =  int(self.enable_lyc_interrupt)    << 6
        value |= int(self.enable_oam_interrupt)    << 5
        value |= int(self.enable_vblank_interrupt) << 4
        value |= int(self.enable_hblank_interrupt) << 3
        value |= int(self.ly == self.lyc)          << 2
        value |= self.mode & 0b10
        value |= self.mode & 0b01
        return value

    def writeSTAT(self, value):
        self.enable_lyc_interrupt    = bool(value & 0b01000000)
        self.enable_oam_interrupt    = bool(value & 0b00100000)
        self.enable_vblank_interrupt = bool(value & 0b00010000)
        self.enable_hblank_interrupt = bool(value & 0b00001000)

    # Scroll Y
    def readSCY(self):
        return self.scy

    def writeSCY(self, value):
        self.scy = value

    # Scroll X
    def readSCX(self):
        return self.scx

    def writeSCX(self, value):
        self.scx = value

    # Y coordinate
    def readLY(self):
        return self.ly

    def writeLY(self, value):
        self.ly = 0

    # Y coordinate compare
    def readLYC(self):
        return self.lyc

    def writeLYC(self, value):
        self.lyc = value

    # Window Y Position
    def readWY(self):
        return self.wy

    def writeWY(self, value):
         self.wy = value

    # Window X Position
    def readWX(self):
        return self.wx

    def writeWX(self, value):
        self.wx = value

    # Background palette data
    def readBGP(self):
        value =  self.bgp_color3 << 6
        value |= self.bgp_color2 << 4
        value |= self.bgp_color1 << 2
        value |= self.bgp_color0
        return value

    def writeBGP(self, value):
        self.bgp_color3 =  value >> 6
        self.bgp_color2 = (value >> 4) & 0b11
        self.bgp_color1 = (value >> 2) & 0b11
        self.bgp_color0 =  value       & 0b11

    # Object palette 0 data
    def readOBP0(self):
        value =  self.obp0_color3 << 6
        value |= self.obp0_color2 << 4
        value |= self.obp0_color1 << 2
        return value

    def writeOBP0(self, value):
        self.obp0_color3 =  value >> 6
        self.obp0_color2 = (value >> 4) & 0b11
        self.obp0_color1 = (value >> 2) & 0b11

    # Object palette 1 data
    def readOBP1(self):
        value =  self.obp1_color3 << 6
        value |= self.obp1_color2 << 4
        value |= self.obp1_color1 << 2
        return value

    def writeOBP1(self, value):
        self.obp1_color3 =  value >> 6
        self.obp1_color2 = (value >> 4) & 0b11
        self.obp1_color1 = (value >> 2) & 0b11

    def writeOAM_DMA(self, value):
        assert(value >= 0 and value < 0xF1)
        source_address = value << 8
        for offset in range(0xA0):
            byte = self.mem.read(source_address + offset)
            self.mem.write(0xFE00 + offset, byte)
