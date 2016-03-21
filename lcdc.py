class LCDC:
    def __init__(self, mem, interrupts):
        self.mem = mem
        self.interrupts = interrupts

        # FF40 bits 7-0
        # w - window
        # bg - background
        self.display_enable             = False
        self.w_tile_map_display_select  = False
        self.w_display_enable           = False
        self.bg_w_tile_select           = False
        self.bg_tile_map_display_select = False
        self.sprite_size                = False
        self.sprite_display_enable      = False
        self.bg_display                 = False

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
        # Transitions: 2 -> 3 -> 0 -> 2 or 1
        
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

        ##FF48 bits
        #color0 is unused because sprites render it as transparent
        self.obp0_color1 = 0
        self.obp0_color2 = 0
        self.obp0_color3 = 0

        ##FF49 bits
        self.obp1_color1 = 0
        self.obp1_color2 = 0
        self.obp1_color3 = 0

    def update(self, cycles):
        self.mode_counter += cycles
        if self.mode == 0:
            if self.mode_counter >= 204:
                self.mode_counter = 0
                self.ly += 1
                if self.ly == 144: #Reached end of screen
                    self.mode = 1
                else:
                    self.mode = 2
        elif self.mode == 1:
            if self.mode_counter >= 4560:
                self.mode_counter = 0
                self.mode = 2
                self.ly = 0
            if self.mode_counter % 456 == 0 and self.mode_counter != 0:
                self.ly += 1
        elif self.mode == 2:
            if self.mode_counter >= 80:
                self.mode_counter = 0
                self.mode = 3
        elif self.mode == 3:
            if self.mode_counter >= 172:
                self.mode_counter = 0
                self.mode = 0
        else:
            assert(False)

        self.updateInterrupts()

    def updateInterrupts(self):
        lyc_interrupt = (self.ly == self.lyc) and self.enable_lyc_interrupt
        oam_interrupt = self.mode == 2 and self.enable_oam_interrupt
        hblank_interrupt = self.mode == 0 and self.enable_hblank_interrupt

        if lyc_interrupt or lyc_interrupt or oam_interrupt or hblank_interrupt:
            self.interrupts.callLCDC()
        elif self.mode == 1 and self.enable_vblank_interrupt:
            self.interrupts.callVBlank()

    # LCD Control
    def readLCDC(self):
        value =  int(self.display_enable)             << 7
        value |= int(self.w_tile_map_display_select)  << 6
        value |= int(self.w_display_enable)           << 5
        value |= int(self.bg_w_tile_select)           << 4
        value |= int(self.bg_tile_map_display_select) << 3
        value |= int(self.sprite_size)                << 2
        value |= int(self.sprite_display_enable)      << 1
        value |= int(self.bg_display)                 << 0
        return value

    def writeLCDC(self, value):
        self.display_enable             = bool(value & 0b10000000)
        self.w_tile_map_display_select  = bool(value & 0b01000000)
        self.w_display_enable           = bool(value & 0b00100000)
        self.bg_w_tile_select           = bool(value & 0b00010000)
        self.bg_tile_map_display_select = bool(value & 0b00001000)
        self.sprite_size                = bool(value & 0b00000100)
        self.sprite_display_enable      = bool(value & 0b00000010)
        self.bg_display                 = bool(value & 0b00000001)

    # LCD Status
    def readSTAT(self):
        value =  int(self.enable_lyc_interrupt)    << 6
        value |= int(self.enable_oam_interrupt)    << 5
        value |= int(self.enable_vblank_interrupt) << 4
        value |= int(self.enable_hblank_interrupt) << 3
        value |= int(self.ly == lyc)               << 2
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

    # Background pallete data
    def readBGP(self):
        value =  self.bgp_color3 << 6
        value |= self.bgp_color2 << 4
        value |= self.bgp_color1 << 2
        value |= self.bgp_color0
        return value

    def writeBGP(self, value):
        self.bgp_color3 =  value >> 6
        self.bgp_color2 = (value >> 4) & 0x11
        self.bgp_color1 = (value >> 2) & 0x11
        self.bgp_color0 =  value       & 0x11

    # Object pallete 0 data
    def readOBP0(self):
        value =  self.obp0_color3 << 6
        value |= self.obp0_color2 << 4
        value |= self.obp0_color1 << 2
        return value

    def writeOBP0(self, value):
        self.obp0_color3 =  value >> 6
        self.obp0_color2 = (value >> 4) & 0x11
        self.obp0_color1 = (value >> 2) & 0x11

    # Object pallete 1 data
    def readOBP1(self):
        value =  self.obp1_color3 << 6
        value |= self.obp1_color2 << 4
        value |= self.obp1_color1 << 2
        return value

    def writeOBP1(self, value):
        self.obp1_color3 =  value >> 6
        self.obp1_color2 = (value >> 4) & 0x11
        self.obp1_color1 = (value >> 2) & 0x11
