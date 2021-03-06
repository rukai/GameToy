import registers
import interrupts
import memory

class CPU:
    def __init__(self, mem, interrupts, debug_instructions, debug_registers):
        self.debug_instructions = debug_instructions
        self.debug_registers = debug_registers
        self.run_state = "RUN" # possible values: RUN, HALT, STOP, QUIT
        self.mem = mem
        self.cycles = 0 # machine cycles
        self.op_desc = "" # Stores a human readable string of the current operation for debugging

        self.a      = registers.RegisterByte(0x0, "A")
        self.f      = registers.RegisterFlag(0xB0, "F")
        self.b      = registers.RegisterByte(0x0, "B")
        self.c      = registers.RegisterByte(0x13, "C")
        self.d      = registers.RegisterByte(0x0, "D")
        self.e      = registers.RegisterByte(0xD8, "E")
        self.h      = registers.RegisterByte(0x1, "H")
        self.l      = registers.RegisterByte(0x4D, "L")
        self.af     = registers.RegisterWord(self.a, self.f, "AF")
        self.bc     = registers.RegisterWord(self.b, self.c, "BC")
        self.de     = registers.RegisterWord(self.d, self.e, "DE")
        self.hl     = registers.RegisterWord(self.h, self.l, "HL")
        self.pc     = registers.RegisterWord.fromValue(0x100, "PC")
        self.sp     = registers.RegisterWord.fromValue(0xFFFE, "SP")

        self.interrupts = interrupts
        interrupts.setCall(self.callBase)

        self.op_table = {
            0x00:         self.nop,
            0x76:         self.halt,
            0x10:         self.stop,

            # Interrupts
            0xF3:         self.di,
            0xFB:         self.ei,

            # Loads
            0x08:         self.ld_Wx,

            0x7F: lambda: self.ld_rr(self.a, self.a),
            0x78: lambda: self.ld_rr(self.a, self.b),
            0x79: lambda: self.ld_rr(self.a, self.c),
            0x7A: lambda: self.ld_rr(self.a, self.d),
            0x7B: lambda: self.ld_rr(self.a, self.e),
            0x7C: lambda: self.ld_rr(self.a, self.h),
            0x7D: lambda: self.ld_rr(self.a, self.l),
            0x7E: lambda: self.ld_rX(self.a, self.hl),
            0x0A: lambda: self.ld_rX(self.a, self.bc),
            0x1A: lambda: self.ld_rX(self.a, self.de),
            0xFA: lambda: self.ld_rW(self.a),
            0xEA: lambda: self.ld_Wr(self.a),

            0x47: lambda: self.ld_rr(self.b, self.a),
            0x40: lambda: self.ld_rr(self.b, self.b),
            0x41: lambda: self.ld_rr(self.b, self.c),
            0x42: lambda: self.ld_rr(self.b, self.d),
            0x43: lambda: self.ld_rr(self.b, self.e),
            0x44: lambda: self.ld_rr(self.b, self.h),
            0x45: lambda: self.ld_rr(self.b, self.l),
            0x46: lambda: self.ld_rX(self.b, self.hl),

            0x4F: lambda: self.ld_rr(self.c, self.a),
            0x48: lambda: self.ld_rr(self.c, self.b),
            0x49: lambda: self.ld_rr(self.c, self.c),
            0x4A: lambda: self.ld_rr(self.c, self.d),
            0x4B: lambda: self.ld_rr(self.c, self.e),
            0x4C: lambda: self.ld_rr(self.c, self.h),
            0x4D: lambda: self.ld_rr(self.c, self.l),
            0x4E: lambda: self.ld_rX(self.c, self.hl),

            0x57: lambda: self.ld_rr(self.d, self.a),
            0x50: lambda: self.ld_rr(self.d, self.b),
            0x51: lambda: self.ld_rr(self.d, self.c),
            0x52: lambda: self.ld_rr(self.d, self.d),
            0x53: lambda: self.ld_rr(self.d, self.e),
            0x54: lambda: self.ld_rr(self.d, self.h),
            0x55: lambda: self.ld_rr(self.d, self.l),
            0x56: lambda: self.ld_rX(self.d, self.hl),

            0x5F: lambda: self.ld_rr(self.e, self.a),
            0x58: lambda: self.ld_rr(self.e, self.b),
            0x59: lambda: self.ld_rr(self.e, self.c),
            0x5A: lambda: self.ld_rr(self.e, self.d),
            0x5B: lambda: self.ld_rr(self.e, self.e),
            0x5C: lambda: self.ld_rr(self.e, self.h),
            0x5D: lambda: self.ld_rr(self.e, self.l),
            0x5E: lambda: self.ld_rX(self.e, self.hl),

            0x67: lambda: self.ld_rr(self.h, self.a),
            0x60: lambda: self.ld_rr(self.h, self.b),
            0x61: lambda: self.ld_rr(self.h, self.c),
            0x62: lambda: self.ld_rr(self.h, self.d),
            0x63: lambda: self.ld_rr(self.h, self.e),
            0x64: lambda: self.ld_rr(self.h, self.h),
            0x65: lambda: self.ld_rr(self.h, self.l),
            0x66: lambda: self.ld_rX(self.h, self.hl),

            0x6F: lambda: self.ld_rr(self.l, self.a),
            0x68: lambda: self.ld_rr(self.l, self.b),
            0x69: lambda: self.ld_rr(self.l, self.c),
            0x6A: lambda: self.ld_rr(self.l, self.d),
            0x6B: lambda: self.ld_rr(self.l, self.e),
            0x6C: lambda: self.ld_rr(self.l, self.h),
            0x6D: lambda: self.ld_rr(self.l, self.l),
            0x6E: lambda: self.ld_rX(self.l, self.hl),

            0x77: lambda: self.ld_Xr(self.hl, self.a),
            0x70: lambda: self.ld_Xr(self.hl, self.b),
            0x71: lambda: self.ld_Xr(self.hl, self.c),
            0x72: lambda: self.ld_Xr(self.hl, self.d),
            0x73: lambda: self.ld_Xr(self.hl, self.e),
            0x74: lambda: self.ld_Xr(self.hl, self.h),
            0x75: lambda: self.ld_Xr(self.hl, self.l),

            0x3E: lambda: self.ld_rb(self.a),
            0x06: lambda: self.ld_rb(self.b),
            0x0E: lambda: self.ld_rb(self.c),
            0x16: lambda: self.ld_rb(self.d),
            0x1E: lambda: self.ld_rb(self.e),
            0x26: lambda: self.ld_rb(self.h),
            0x2E: lambda: self.ld_rb(self.l),
            0xE0:         self.ldh_br,
            0xF0:         self.ldh_rb,

            0x36: lambda: self.ld_Xb(self.hl),
            0x02: lambda: self.ld_Xr(self.bc, self.a),
            0x12: lambda: self.ld_Xr(self.de, self.a),
            0x3A:         self.ldd_rX,
            0x32:         self.ldd_Xr,
            0x2A:         self.ldi_rX,
            0x22:         self.ldi_Xr,

            0x01: lambda: self.ld_xw(self.bc),
            0x11: lambda: self.ld_xw(self.de),
            0x21: lambda: self.ld_xw(self.hl),
            0x31: lambda: self.ld_xw(self.sp),
            0xF9: lambda: self.ld_xx(self.sp, self.hl),

            0xE2:         self.ldh_Rr,
            0xF2:         self.ldh_rR,

            # Stack operations
            0xC5: lambda: self.push_x(self.bc),
            0xD5: lambda: self.push_x(self.de),
            0xE5: lambda: self.push_x(self.hl),
            0xF5: lambda: self.push_x(self.af),

            0xC1: lambda: self.pop_x(self.bc),
            0xD1: lambda: self.pop_x(self.de),
            0xE1: lambda: self.pop_x(self.hl),
            0xF1: lambda: self.pop_x(self.af),

            # Compare
            0xBF: lambda: self.cp_r(self.a),
            0xB8: lambda: self.cp_r(self.b),
            0xB9: lambda: self.cp_r(self.c),
            0xBA: lambda: self.cp_r(self.d),
            0xBB: lambda: self.cp_r(self.e),
            0xBC: lambda: self.cp_r(self.h),
            0xBD: lambda: self.cp_r(self.l),
            0xBE: lambda: self.cp_X(self.hl),
            0xFE:         self.cp_b,

            # Jumps
            0xC3:         self.jp_w,
            0xE9: lambda: self.jp_X(self.hl),
            0xC2: lambda: self.jp_fw("NZ"),
            0xCA: lambda: self.jp_fw("Z"),
            0xD2: lambda: self.jp_fw("NC"),
            0xDA: lambda: self.jp_fw("C"),

            0x18:         self.jr_b,
            0x20: lambda: self.jr_fb("NZ"),
            0x28: lambda: self.jr_fb("Z"),
            0x30: lambda: self.jr_fb("NC"),
            0x38: lambda: self.jr_fb("C"),

            # Calls
            0xCD:         self.call_w,
            0xC4: lambda: self.call_fw("NZ"),
            0xCC: lambda: self.call_fw("Z"),
            0xD4: lambda: self.call_fw("NC"),
            0xDC: lambda: self.call_fw("C"),

            # Returns
            0xC9:         self.ret,
            0xD9:         self.reti,
            0xC0: lambda: self.ret_f("NZ"),
            0xC8: lambda: self.ret_f("Z"),
            0xD0: lambda: self.ret_f("NC"),
            0xD8: lambda: self.ret_f("C"),

            # Restarts
            0xC7: lambda: self.rst_b(0x00),
            0xCF: lambda: self.rst_b(0x08),
            0xD7: lambda: self.rst_b(0x10),
            0xDF: lambda: self.rst_b(0x18),
            0xE7: lambda: self.rst_b(0x20),
            0xEF: lambda: self.rst_b(0x28),
            0xF7: lambda: self.rst_b(0x30),
            0xFF: lambda: self.rst_b(0x38),

            # ADD
            0x87: lambda: self.add_rr(self.a),
            0x80: lambda: self.add_rr(self.b),
            0x81: lambda: self.add_rr(self.c),
            0x82: lambda: self.add_rr(self.d),
            0x83: lambda: self.add_rr(self.e),
            0x84: lambda: self.add_rr(self.h),
            0x85: lambda: self.add_rr(self.l),
            0x86: lambda: self.add_rX(self.hl),
            0xC6:         self.add_rb,

            0x09: lambda: self.add_xx(self.bc),
            0x19: lambda: self.add_xx(self.de),
            0x29: lambda: self.add_xx(self.hl),
            0x39: lambda: self.add_xx(self.sp),
            0xE8:         self.add_xb,

            0x8f: lambda: self.adc_rr(self.a),
            0x88: lambda: self.adc_rr(self.b),
            0x89: lambda: self.adc_rr(self.c),
            0x8A: lambda: self.adc_rr(self.d),
            0x8B: lambda: self.adc_rr(self.e),
            0x8C: lambda: self.adc_rr(self.h),
            0x8D: lambda: self.adc_rr(self.l),
            0x8E: lambda: self.adc_rX(self.hl),
            0xCE:         self.adc_rb,

            # SUB
            0x97: lambda: self.sub_rr(self.a),
            0x90: lambda: self.sub_rr(self.b),
            0x91: lambda: self.sub_rr(self.c),
            0x92: lambda: self.sub_rr(self.d),
            0x93: lambda: self.sub_rr(self.e),
            0x94: lambda: self.sub_rr(self.h),
            0x95: lambda: self.sub_rr(self.l),
            0x96: lambda: self.sub_rX(self.hl),
            0xD6:         self.sub_rb,

            0x9f: lambda: self.sub_rr(self.a),
            0x98: lambda: self.sub_rr(self.b),
            0x99: lambda: self.sub_rr(self.c),
            0x9A: lambda: self.sub_rr(self.d),
            0x9B: lambda: self.sub_rr(self.e),
            0x9C: lambda: self.sub_rr(self.h),
            0x9D: lambda: self.sub_rr(self.l),
            0x9E: lambda: self.sub_rX(self.hl),
            0xDE:         self.sub_rb,

            # AND
            0xA7: lambda: self.and_r(self.a),
            0xA0: lambda: self.and_r(self.b),
            0xA1: lambda: self.and_r(self.c),
            0xA2: lambda: self.and_r(self.d),
            0xA3: lambda: self.and_r(self.e),
            0xA4: lambda: self.and_r(self.h),
            0xA5: lambda: self.and_r(self.l),
            0xA6: lambda: self.and_X(self.hl),
            0xE6:         self.and_b,

            # OR
            0xB7: lambda: self.or_r(self.a),
            0xB0: lambda: self.or_r(self.b),
            0xB1: lambda: self.or_r(self.c),
            0xB2: lambda: self.or_r(self.d),
            0xB3: lambda: self.or_r(self.e),
            0xB4: lambda: self.or_r(self.h),
            0xB5: lambda: self.or_r(self.l),
            0xB6: lambda: self.or_X(self.hl),
            0xF6:         self.or_b,

            # XOR
            0xAF: lambda: self.xor_r(self.a),
            0xA8: lambda: self.xor_r(self.b),
            0xA9: lambda: self.xor_r(self.c),
            0xAA: lambda: self.xor_r(self.d),
            0xAB: lambda: self.xor_r(self.e),
            0xAC: lambda: self.xor_r(self.h),
            0xAD: lambda: self.xor_r(self.l),
            0xAE: lambda: self.xor_X(self.hl),
            0xEE:         self.xor_b,

            # INC
            0x3C: lambda: self.inc_r(self.a),
            0x04: lambda: self.inc_r(self.b),
            0x0C: lambda: self.inc_r(self.c),
            0x14: lambda: self.inc_r(self.d),
            0x1C: lambda: self.inc_r(self.e),
            0x24: lambda: self.inc_r(self.h),
            0x2C: lambda: self.inc_r(self.l),
            0x03: lambda: self.inc_x(self.bc),
            0x13: lambda: self.inc_x(self.de),
            0x23: lambda: self.inc_x(self.hl),
            0x33: lambda: self.inc_x(self.sp),
            0x34:         self.inc_X,

            # DEC
            0x3D: lambda: self.dec_r(self.a),
            0x05: lambda: self.dec_r(self.b),
            0x0D: lambda: self.dec_r(self.c),
            0x15: lambda: self.dec_r(self.d),
            0x1D: lambda: self.dec_r(self.e),
            0x25: lambda: self.dec_r(self.h),
            0x2D: lambda: self.dec_r(self.l),
            0x0B: lambda: self.dec_x(self.bc),
            0x1B: lambda: self.dec_x(self.de),
            0x2B: lambda: self.dec_x(self.hl),
            0x3B: lambda: self.dec_x(self.sp),
            0x35:         self.dec_X,

            # Misc ALU
            0x27:         self.daa,
            0x2F:         self.cpl,


            # Rotates
            0x07:         self.rlca,
            0x0F:         self.rrca,
            0x17:         self.rla,
            0x1F:         self.rra,
            0xCB:         self.cb_prefix,
        }

        self.cb_op_table = {
            # Rotates
            0x07: lambda: self.rlc_r(self.a),
            0x00: lambda: self.rlc_r(self.b),
            0x01: lambda: self.rlc_r(self.c),
            0x02: lambda: self.rlc_r(self.d),
            0x03: lambda: self.rlc_r(self.e),
            0x04: lambda: self.rlc_r(self.h),
            0x05: lambda: self.rlc_r(self.l),
            0x06:         self.rlc_X,

            0x17: lambda: self.rl_r(self.a),
            0x10: lambda: self.rl_r(self.b),
            0x11: lambda: self.rl_r(self.c),
            0x12: lambda: self.rl_r(self.d),
            0x13: lambda: self.rl_r(self.e),
            0x14: lambda: self.rl_r(self.h),
            0x15: lambda: self.rl_r(self.l),
            0x16:         self.rl_X,

            0x0F: lambda: self.rrc_r(self.a),
            0x08: lambda: self.rrc_r(self.b),
            0x09: lambda: self.rrc_r(self.c),
            0x0A: lambda: self.rrc_r(self.d),
            0x0B: lambda: self.rrc_r(self.e),
            0x0C: lambda: self.rrc_r(self.h),
            0x0D: lambda: self.rrc_r(self.l),
            0x0E:         self.rrc_X,

            0x1F: lambda: self.rr_r(self.a),
            0x18: lambda: self.rr_r(self.b),
            0x19: lambda: self.rr_r(self.c),
            0x1A: lambda: self.rr_r(self.d),
            0x1B: lambda: self.rr_r(self.e),
            0x1C: lambda: self.rr_r(self.h),
            0x1D: lambda: self.rr_r(self.l),
            0x1E:         self.rr_X,

            # Shifts
            0x27: lambda: self.sla_r(self.a),
            0x20: lambda: self.sla_r(self.b),
            0x21: lambda: self.sla_r(self.c),
            0x22: lambda: self.sla_r(self.d),
            0x23: lambda: self.sla_r(self.e),
            0x24: lambda: self.sla_r(self.h),
            0x25: lambda: self.sla_r(self.l),
            0x26: lambda: self.sla_X(self.hl),

            0x2F: lambda: self.sra_r(self.a),
            0x28: lambda: self.sra_r(self.b),
            0x29: lambda: self.sra_r(self.c),
            0x2A: lambda: self.sra_r(self.d),
            0x2B: lambda: self.sra_r(self.e),
            0x2C: lambda: self.sra_r(self.h),
            0x2D: lambda: self.sra_r(self.l),
            0x2E: lambda: self.sra_X(self.hl),

            0x3F: lambda: self.srl_r(self.a),
            0x38: lambda: self.srl_r(self.b),
            0x39: lambda: self.srl_r(self.c),
            0x3A: lambda: self.srl_r(self.d),
            0x3B: lambda: self.srl_r(self.e),
            0x3C: lambda: self.srl_r(self.h),
            0x3D: lambda: self.srl_r(self.l),
            0x3E: lambda: self.srl_X(self.hl),

            # Swaps
            0x37: lambda: self.swap_r(self.a),
            0x30: lambda: self.swap_r(self.b),
            0x31: lambda: self.swap_r(self.c),
            0x32: lambda: self.swap_r(self.d),
            0x33: lambda: self.swap_r(self.e),
            0x34: lambda: self.swap_r(self.h),
            0x35: lambda: self.swap_r(self.l),
            0x36: lambda: self.swap_X,

            # Set Bit
            0xC7: lambda: self.set_ir(0, self.a),
            0xC0: lambda: self.set_ir(0, self.b),
            0xC1: lambda: self.set_ir(0, self.c),
            0xC2: lambda: self.set_ir(0, self.d),
            0xC3: lambda: self.set_ir(0, self.e),
            0xC4: lambda: self.set_ir(0, self.h),
            0xC5: lambda: self.set_ir(0, self.l),
            0xC6: lambda: self.set_iX(0, self.hl),

            0xCF: lambda: self.set_ir(1, self.a),
            0xC8: lambda: self.set_ir(1, self.b),
            0xC9: lambda: self.set_ir(1, self.c),
            0xCA: lambda: self.set_ir(1, self.d),
            0xCB: lambda: self.set_ir(1, self.e),
            0xCC: lambda: self.set_ir(1, self.h),
            0xCD: lambda: self.set_ir(1, self.l),
            0xCE: lambda: self.set_iX(1, self.hl),

            0xD7: lambda: self.set_ir(2, self.a),
            0xD0: lambda: self.set_ir(2, self.b),
            0xD1: lambda: self.set_ir(2, self.c),
            0xD2: lambda: self.set_ir(2, self.d),
            0xD3: lambda: self.set_ir(2, self.e),
            0xD4: lambda: self.set_ir(2, self.h),
            0xD5: lambda: self.set_ir(2, self.l),
            0xD6: lambda: self.set_iX(2, self.hl),

            0xDF: lambda: self.set_ir(3, self.a),
            0xD8: lambda: self.set_ir(3, self.b),
            0xD9: lambda: self.set_ir(3, self.c),
            0xDA: lambda: self.set_ir(3, self.d),
            0xDB: lambda: self.set_ir(3, self.e),
            0xDC: lambda: self.set_ir(3, self.h),
            0xDD: lambda: self.set_ir(3, self.l),
            0xDE: lambda: self.set_iX(3, self.hl),
            
            0xE7: lambda: self.set_ir(4, self.a),
            0xE0: lambda: self.set_ir(4, self.b),
            0xE1: lambda: self.set_ir(4, self.c),
            0xE2: lambda: self.set_ir(4, self.d),
            0xE3: lambda: self.set_ir(4, self.e),
            0xE4: lambda: self.set_ir(4, self.h),
            0xE5: lambda: self.set_ir(4, self.l),
            0xE6: lambda: self.set_iX(4, self.hl),

            0xEF: lambda: self.set_ir(5, self.a),
            0xE8: lambda: self.set_ir(5, self.b),
            0xE9: lambda: self.set_ir(5, self.c),
            0xEA: lambda: self.set_ir(5, self.d),
            0xEB: lambda: self.set_ir(5, self.e),
            0xEC: lambda: self.set_ir(5, self.h),
            0xED: lambda: self.set_ir(5, self.l),
            0xEE: lambda: self.set_iX(5, self.hl),

            0xF7: lambda: self.set_ir(6, self.a),
            0xF0: lambda: self.set_ir(6, self.b),
            0xF1: lambda: self.set_ir(6, self.c),
            0xF2: lambda: self.set_ir(6, self.d),
            0xF3: lambda: self.set_ir(6, self.e),
            0xF4: lambda: self.set_ir(6, self.h),
            0xF5: lambda: self.set_ir(6, self.l),
            0xF6: lambda: self.set_iX(6, self.hl),

            0xFF: lambda: self.set_ir(7, self.a),
            0xF8: lambda: self.set_ir(7, self.b),
            0xF9: lambda: self.set_ir(7, self.c),
            0xFA: lambda: self.set_ir(7, self.d),
            0xFB: lambda: self.set_ir(7, self.e),
            0xFC: lambda: self.set_ir(7, self.h),
            0xFD: lambda: self.set_ir(7, self.l),
            0xFE: lambda: self.set_iX(7, self.hl),

            # Reset Bit
            0x87: lambda: self.res_ir(0, self.a),
            0x80: lambda: self.res_ir(0, self.b),
            0x81: lambda: self.res_ir(0, self.c),
            0x82: lambda: self.res_ir(0, self.d),
            0x83: lambda: self.res_ir(0, self.e),
            0x84: lambda: self.res_ir(0, self.h),
            0x85: lambda: self.res_ir(0, self.l),
            0x86: lambda: self.res_iX(0, self.hl),

            0x8F: lambda: self.res_ir(1, self.a),
            0x88: lambda: self.res_ir(1, self.b),
            0x89: lambda: self.res_ir(1, self.c),
            0x8A: lambda: self.res_ir(1, self.d),
            0x8B: lambda: self.res_ir(1, self.e),
            0x8C: lambda: self.res_ir(1, self.h),
            0x8D: lambda: self.res_ir(1, self.l),
            0x8E: lambda: self.res_iX(1, self.hl),

            0x97: lambda: self.res_ir(2, self.a),
            0x90: lambda: self.res_ir(2, self.b),
            0x91: lambda: self.res_ir(2, self.c),
            0x92: lambda: self.res_ir(2, self.d),
            0x93: lambda: self.res_ir(2, self.e),
            0x94: lambda: self.res_ir(2, self.h),
            0x95: lambda: self.res_ir(2, self.l),
            0x96: lambda: self.res_iX(2, self.hl),

            0x9F: lambda: self.res_ir(3, self.a),
            0x98: lambda: self.res_ir(3, self.b),
            0x99: lambda: self.res_ir(3, self.c),
            0x9A: lambda: self.res_ir(3, self.d),
            0x9B: lambda: self.res_ir(3, self.e),
            0x9C: lambda: self.res_ir(3, self.h),
            0x9D: lambda: self.res_ir(3, self.l),
            0x9E: lambda: self.res_iX(3, self.hl),
            
            0xA7: lambda: self.res_ir(4, self.a),
            0xA0: lambda: self.res_ir(4, self.b),
            0xA1: lambda: self.res_ir(4, self.c),
            0xA2: lambda: self.res_ir(4, self.d),
            0xA3: lambda: self.res_ir(4, self.e),
            0xA4: lambda: self.res_ir(4, self.h),
            0xA5: lambda: self.res_ir(4, self.l),
            0xA6: lambda: self.res_iX(4, self.hl),

            0xAF: lambda: self.res_ir(5, self.a),
            0xA8: lambda: self.res_ir(5, self.b),
            0xA9: lambda: self.res_ir(5, self.c),
            0xAA: lambda: self.res_ir(5, self.d),
            0xAB: lambda: self.res_ir(5, self.e),
            0xAC: lambda: self.res_ir(5, self.h),
            0xAD: lambda: self.res_ir(5, self.l),
            0xAE: lambda: self.res_iX(5, self.hl),

            0xB7: lambda: self.res_ir(6, self.a),
            0xB0: lambda: self.res_ir(6, self.b),
            0xB1: lambda: self.res_ir(6, self.c),
            0xB2: lambda: self.res_ir(6, self.d),
            0xB3: lambda: self.res_ir(6, self.e),
            0xB4: lambda: self.res_ir(6, self.h),
            0xB5: lambda: self.res_ir(6, self.l),
            0xB6: lambda: self.res_iX(6, self.hl),

            0xBF: lambda: self.res_ir(7, self.a),
            0xB8: lambda: self.res_ir(7, self.b),
            0xB9: lambda: self.res_ir(7, self.c),
            0xBA: lambda: self.res_ir(7, self.d),
            0xBB: lambda: self.res_ir(7, self.e),
            0xBC: lambda: self.res_ir(7, self.h),
            0xBD: lambda: self.res_ir(7, self.l),
            0xBE: lambda: self.res_iX(7, self.hl),

            # Get Bit
            0x47: lambda: self.bit_ir(0, self.a),
            0x40: lambda: self.bit_ir(0, self.b),
            0x41: lambda: self.bit_ir(0, self.c),
            0x42: lambda: self.bit_ir(0, self.d),
            0x43: lambda: self.bit_ir(0, self.e),
            0x44: lambda: self.bit_ir(0, self.h),
            0x45: lambda: self.bit_ir(0, self.l),
            0x46: lambda: self.bit_iX(0, self.hl),

            0x4F: lambda: self.bit_ir(1, self.a),
            0x48: lambda: self.bit_ir(1, self.b),
            0x49: lambda: self.bit_ir(1, self.c),
            0x4A: lambda: self.bit_ir(1, self.d),
            0x4B: lambda: self.bit_ir(1, self.e),
            0x4C: lambda: self.bit_ir(1, self.h),
            0x4D: lambda: self.bit_ir(1, self.l),
            0x4E: lambda: self.bit_iX(1, self.hl),

            0x57: lambda: self.bit_ir(2, self.a),
            0x50: lambda: self.bit_ir(2, self.b),
            0x51: lambda: self.bit_ir(2, self.c),
            0x52: lambda: self.bit_ir(2, self.d),
            0x53: lambda: self.bit_ir(2, self.e),
            0x54: lambda: self.bit_ir(2, self.h),
            0x55: lambda: self.bit_ir(2, self.l),
            0x56: lambda: self.bit_iX(2, self.hl),

            0x5F: lambda: self.bit_ir(3, self.a),
            0x58: lambda: self.bit_ir(3, self.b),
            0x59: lambda: self.bit_ir(3, self.c),
            0x5A: lambda: self.bit_ir(3, self.d),
            0x5B: lambda: self.bit_ir(3, self.e),
            0x5C: lambda: self.bit_ir(3, self.h),
            0x5D: lambda: self.bit_ir(3, self.l),
            0x5E: lambda: self.bit_iX(3, self.hl),

            0x67: lambda: self.bit_ir(4, self.a),
            0x60: lambda: self.bit_ir(4, self.b),
            0x61: lambda: self.bit_ir(4, self.c),
            0x62: lambda: self.bit_ir(4, self.d),
            0x63: lambda: self.bit_ir(4, self.e),
            0x64: lambda: self.bit_ir(4, self.h),
            0x65: lambda: self.bit_ir(4, self.l),
            0x66: lambda: self.bit_iX(4, self.hl),

            0x6F: lambda: self.bit_ir(5, self.a),
            0x68: lambda: self.bit_ir(5, self.b),
            0x69: lambda: self.bit_ir(5, self.c),
            0x6A: lambda: self.bit_ir(5, self.d),
            0x6B: lambda: self.bit_ir(5, self.e),
            0x6C: lambda: self.bit_ir(5, self.h),
            0x6D: lambda: self.bit_ir(5, self.l),
            0x6E: lambda: self.bit_iX(5, self.hl),

            0x77: lambda: self.bit_ir(6, self.a),
            0x70: lambda: self.bit_ir(6, self.b),
            0x71: lambda: self.bit_ir(6, self.c),
            0x72: lambda: self.bit_ir(6, self.d),
            0x73: lambda: self.bit_ir(6, self.e),
            0x74: lambda: self.bit_ir(6, self.h),
            0x75: lambda: self.bit_ir(6, self.l),
            0x76: lambda: self.bit_iX(6, self.hl),

            0x7F: lambda: self.bit_ir(7, self.a),
            0x78: lambda: self.bit_ir(7, self.b),
            0x79: lambda: self.bit_ir(7, self.c),
            0x7A: lambda: self.bit_ir(7, self.d),
            0x7B: lambda: self.bit_ir(7, self.e),
            0x7C: lambda: self.bit_ir(7, self.h),
            0x7D: lambda: self.bit_ir(7, self.l),
            0x7E: lambda: self.bit_iX(7, self.hl),
        }

    def run(self):
        self.op_desc = "main_loop" #dummy value used to check if set
        instruction = self.mem.read(int(self.pc))

        if instruction in self.op_table:
            self.op_table[instruction]()
        else:
            msg = "{}: Instruction {} not implemented! AAAAGH!! ... I'm dead ..."
            print(msg.format(asmHex(int(self.pc), 4), asmHex(instruction)))
            self.pc += 1
            self.run_state = "QUIT"
            return

        if self.op_desc == "main_loop":
            print("No op_desc for:", asmHex(instruction))
        
        if self.debug_registers:
            self.displayRegisters()

    def cb_prefix(self):
        self.pc += 1
        self.op_desc = "cb_prefix"
        instruction = self.mem.read(int(self.pc))
        if instruction in self.cb_op_table:
            self.cb_op_table[instruction]()
        else:
            msg = "{}: Instruction $CB+{} not implemented! AAAAGH!! ... I'm dead ..."
            print(msg.format(asmHex(int(self.pc), 4), asmHex(instruction)))
            self.run_state = "QUIT"
            return

        if self.op_desc == "cb_prefix":
            print("No op_desc for $CB+" + asmHex(instruction))

    def setOpDesc(self, name, arg1="", arg2=""):
        if self.debug_instructions:
            self.op_desc = "{}: {}".format(asmHex(int(self.pc), 4), name)
            if arg1:
                self.op_desc += " " + arg1
            if arg2:
                self.op_desc += ", " + arg2
            print(self.op_desc)
        else:
            self.op_desc = ""

    def displayRegisters(self):
        print("------------------------------------------------")
        print("a:", asmHex(int(self.a)))
        print("b:", asmHex(int(self.b)))
        print("c:", asmHex(int(self.c)))
        print("d:", asmHex(int(self.d)))
        print("e:", asmHex(int(self.e)))
        print("f:", asmHex(int(self.f)), "0b" + format(int(self.f), '08b'))
        print("h:", asmHex(int(self.h)))
        print("l:", asmHex(int(self.l)))
        print("pc:", asmHex(int(self.pc), 4))
        print("sp:", asmHex(int(self.sp), 4))
        print("ROM bank", self.mem.rom_bank)
        print("Cart RAM bank", self.mem.cart_ram_bank)
        print("------------------------------------------------")

    def popCycles(self):
        value = self.cycles
        self.cycles = 0
        return value

    def checkFlag(self, flagType):
        if flagType == "NZ":
            return not self.f.getZero()
        elif flagType == "Z":
            return self.f.getZero()
        elif flagType == "NC":
            return not self.f.getCarry()
        elif flagType == "C":
            return self.f.getCarry()
        elif flagType == "Always":
            return True
        else:
            assert(False)

    def getImmediateWord(self):
        value = self.mem.read(int(self.pc)+1) + (self.mem.read(int(self.pc)+2) << 8)
        assert(value <= 0xFFFF)
        return value

    def getImmediateByte(self):
        value = self.mem.read(int(self.pc)+1)
        assert(value <= 0xFF)
        return value

    def getImmediateSignedByte(self):
        value = self.mem.readSigned(int(self.pc)+1)
        assert(value <= 0xFF)
        return value

    # To keep the op_table aligned and for documentation purposes,
    # The following are used to refer to operands:
    #   r - register
    #   R - dereference ($FF00+register)
    #   x - 16 bit register
    #   X - dereferenced 16 bit register
    #   b - immediate byte (8 bit value)
    #   w - immediate word (16 bit value)
    #   W - dereferenced immediate word
    #   f - flag conditional
    #   i - index to register bit
    #
    # They are not used to refer to the arguments that the functions
    # used to emulate the operation take instead they refer to the
    # operands required for that operation in Assembly.

    def nop(self):
        self.setOpDesc("NOP")
        self.pc += 1
        self.cycles += 1

    def halt(self):
        self.setOpDesc("HALT")

        if self.interrupts.getIME():
            self.run_state = "HALT"
        # 'Skip' bug for next instruction is unimplemented

        self.pc += 1
        self.cycles += 1

    def stop(self):
        self.setOpDesc("STOP")
        self.run_state = "STOP"
        self.pc += 1
        self.cycles += 1

    # Interrupts
    def di(self):
        self.setOpDesc("DI")
        self.pc += 1
        self.cycles += 1
        self.interrupts.setIME(False)

    def ei(self):
        self.setOpDesc("EI")
        self.pc += 1
        self.cycles += 1
        self.interrupts.setIME(True)

    # Loads
    def ld_Wx(self):
        W = self.getImmediateWord()
        self.setOpDesc("LD", "({})".format(asmHex(W)), "SP")
        value = int(self.sp)
        self.mem.write(W, value & 0xFF)
        self.mem.write(W + 1, (value >> 8) & 0xFF)

        self.pc += 3
        self.cycles += 5

    def ld_rr(self, r1, r2):
        self.setOpDesc("LD", r1.getName(), r2.getName())
        r1.set(int(r2))
        self.pc += 1
        self.cycles += 1

    def ld_rW(self, r):
        W = self.getImmediateWord()
        self.setOpDesc("LD", r.getName(), "({})".format(asmHex(W)))
        r.set(self.mem.read(W))
        self.pc += 3
        self.cycles += 4

    def ld_rX(self, r, X):
        self.setOpDesc("LD", r.getName(), "({})".format(X.getName()))
        r.set(self.mem.read(int(X)))
        self.pc += 1
        self.cycles += 2

    def ld_rb(self, r):
        b = self.getImmediateByte()
        self.setOpDesc("LD", r.getName(), asmHex(b))
        r.set(b)
        self.pc += 2
        self.cycles += 2

    def ld_Xb(self, X):
        b = self.getImmediateByte()
        self.setOpDesc("LD", "({})".format(X.getName()), asmHex(b))
        self.mem.write(int(X), b)
        self.pc += 2
        self.cycles += 3

    def ld_Xr(self, X, r):
        self.setOpDesc("LD",  "({})".format(X.getName()), r.getName())
        self.mem.write(int(X), int(r))
        self.pc += 1
        self.cycles += 2

    def ld_xw(self, x):
        w = self.getImmediateWord()
        self.setOpDesc("LD", x.getName(), asmHex(w, 4))
        x.set(w)
        self.pc += 3
        self.cycles += 3

    def ld_xx(self, x1, x2):
        self.setOpDesc("LD", x1.getName(), x2.getName())
        x1.set(int(x2))
        self.pc += 1
        self.cycles += 2

    def ld_Wr(self, r):
        W = self.getImmediateWord()
        self.setOpDesc("LD", "({})".format(asmHex(W, 4)), r.getName())
        self.mem.write(W, int(r))
        self.pc += 3
        self.cycles += 4

    def ldd_rX(self):
        self.setOpDesc("LDD", "A", "(HL)")
        self.a.set(self.mem.read(int(self.hl)))
        self.hl -= 1
        self.pc += 1
        self.cycles += 2

    def ldd_Xr(self):
        self.setOpDesc("LDD", "(HL)", "A")
        self.mem.write(int(self.hl), int(self.a))
        self.hl -= 1
        self.pc += 1
        self.cycles += 2

    def ldi_rX(self):
        self.setOpDesc("LDI", "A", "(HL)")
        self.a.set(self.mem.read(int(self.hl)))
        self.hl += 1
        self.pc += 1
        self.cycles += 2

    def ldi_Xr(self):
        self.setOpDesc("LDI", "(HL)", "A")
        self.mem.write(int(self.hl), int(self.a))
        self.hl += 1
        self.pc += 1
        self.cycles += 2

    def ldh_rR(self):
        self.setOpDesc("LD", "A", "($FF00+C)")
        address = 0xFF00 + int(self.c)
        self.a.set(self.mem.read(address))
        self.pc += 1
        self.cycles += 2

    def ldh_Rr(self):
        self.setOpDesc("LD", "($FF00+C)", "A")
        address = 0xFF00 + int(self.c)
        self.mem.write(address, int(self.a))
        self.pc += 1
        self.cycles += 2

    def ldh_br(self):
        b = self.getImmediateByte()
        self.setOpDesc("LD", "($FF00+{})".format(asmHex(b)), "A")
        address = 0xFF00 + b
        self.mem.write(address, int(self.a))
        self.pc += 2
        self.cycles += 3

    def ldh_rb(self):
        b = self.getImmediateByte()
        address = 0xFF00 + b
        self.setOpDesc("LD", "A", "($FF00+{})".format(asmHex(b)))
        self.a.set(self.mem.read(address))
        self.pc += 2
        self.cycles += 3

    # Stack Operations
    def push_x(self, x):
        self.setOpDesc("PUSH", x.getName())
        self.sp -= 1
        self.mem.write(int(self.sp), int(x.r1))
        self.sp -= 1
        self.mem.write(int(self.sp), int(x.r2))
        self.pc += 1
        self.cycles += 4

    def pop_x(self, x):
        self.setOpDesc("POP", x.getName())
        x.r2.set(self.mem.read(int(self.sp)))
        self.sp += 1
        x.r1.set(self.mem.read(int(self.sp)))
        self.sp += 1
        self.pc += 1
        self.cycles += 3

    # Compare
    def cpBase(self, byte):
        value = int(self.a) - byte
        new_value = value % 0x100
        self.f.setZero(new_value == 0)
        self.f.setSubtract(True)
        self.f.setHalfCarry(bool(new_value & 0b00010000)) #TODO: VERIFY
        self.f.setCarry(value != new_value)

    def cp_r(self, r):
        self.setOpDesc("CP", r.getName())
        self.cpBase(int(r))
        self.pc += 1
        self.cycles += 1

    def cp_X(self, X):
        self.setOpDesc("CP", "({})".format(X.getName()))
        self.cpBase(self.mem.read(int(X)))
        self.pc += 1
        self.cycles += 2

    def cp_b(self):
        b = self.getImmediateByte()
        self.setOpDesc("CP", asmHex(b))
        self.cpBase(b)
        self.pc += 2
        self.cycles += 2

    # Jumps
    def jp_w(self):
        w = self.getImmediateWord()
        self.setOpDesc("JP", asmHex(w, 4))
        self.pc.set(w)
        self.cycles += 3

    def jp_X(self, X):
        self.setOpDesc("JP", "({})".format(X.getName()))
        self.pc.set(int(X))
        self.cycles += 1

    def jp_fw(self, f):
        w = self.getImmediateWord()
        self.setOpDesc("JP", f, asmHex(w, 4))
        if self.checkFlag(f):
            self.pc.set(w)
        else:
            self.pc += 3
        self.cycles += 3

    def jr_b(self):
        b = self.getImmediateSignedByte()
        self.setOpDesc("JR", asmHex(b))
        self.pc += 2 + b
        self.cycles += 2

    def jr_fb(self, f):
        b = self.getImmediateSignedByte()
        self.setOpDesc("JR", f, asmHex(b))
        self.pc += 2
        if self.checkFlag(f):
            self.pc += b
        self.cycles += 2

    # Calls
    def callBase(self, location):
        self.sp -= 1
        self.mem.write(int(self.sp), int(self.pc.r1))
        self.sp -= 1
        self.mem.write(int(self.sp), int(self.pc.r2))
        self.pc.set(location)
        self.run_state = "RUN"

    def call_w(self):
        w = self.getImmediateWord()
        self.setOpDesc("CALL", asmHex(w, 4))
        
        self.pc += 3
        self.callBase(w)
        self.cycles += 3

    def call_fw(self, f):
        w = self.getImmediateWord()
        self.setOpDesc("CALL", f, asmHex(w, 4))

        self.pc += 3
        if self.checkFlag(f):
            self.callBase(w)
            self.cycles += 6
        else:
            self.cycles += 3

    # Returns
    def retBase(self):
        self.pc.r2.set(self.mem.read(int(self.sp)))
        self.sp += 1
        self.pc.r1.set(self.mem.read(int(self.sp)))
        self.sp += 1

    def ret(self):
        self.setOpDesc("RET")
        self.retBase()
        self.cycles += 4

    def ret_f(self, f):
        self.setOpDesc("RET", f)
        if self.checkFlag(f):
            self.retBase()
            self.cycles += 4
        else:
            self.pc += 1
            self.cycles += 2

    def reti(self):
        self.setOpDesc("RETI")
        self.retBase()
        self.cycles += 4
        self.interrupts.setIME(True)

    # Restart
    def rst_b(self, location):
        self.setOpDesc("RST", asmHex(location))
        self.pc += 1
        self.callBase(location)
        self.cycles += 8

    # ADD
    def addBase(self, byte):
        value = int(self.a) + byte
        newValue = value % 0x100
        self.a.set(newValue)
        self.f.setZero(value == 0)
        self.f.setSubtract(False)
        self.f.setHalfCarry(self.a.getBit(4))
        self.f.setCarry(value != newValue)

    def add_rr(self, r):
        self.setOpDesc("ADD", "A", r.getName())
        self.addBase(int(r))
        self.pc += 1
        self.cycles += 1

    def add_rX(self, X):
        self.setOpDesc("ADD", "A", "({})".format(X.getName()))
        self.addBase(self.mem.read(int(X)))
        self.pc += 1
        self.cycles += 2

    def add_rb(self):
        b = self.getImmediateByte()
        self.setOpDesc("ADD", "A", asmHex(b))
        self.addBase(b)
        self.pc += 2
        self.cycles += 2

    def adc_rr(self, r):
        self.setOpDesc("ADC", "A", r.getName())
        self.addBase(int(r) + int(self.f.getCarry()))
        self.pc += 1
        self.cycles += 1

    def adc_rX(self, X):
        self.setOpDesc("ADC", "A", "({})".format(X.getName()))
        self.addBase(self.mem.read(int(X)) + int(self.f.getCarry()))
        self.pc += 1
        self.cycles += 2

    def adc_rb(self):
        b = self.getImmediateByte()
        self.setOpDesc("ADC", "A", asmHex(b))
        self.addBase(b + int(self.f.getCarry()))
        self.pc += 2
        self.cycles += 2

    # 16-bit ADD
    def add_xx(self, x2):
        self.setOpDesc("ADD", "HL", x2.getName())
        value = (int(self.hl) + int(x2)) % 0x10000
        self.pc += 1
        self.cycles += 2
        self.f.setSubtract(False)
        self.f.setHalfCarry(bool(value & (1 << 12)))
        self.f.setCarry(value != int(self.hl))
        self.hl.set(value)

    def add_xb(self):
        b = self.getImmediateSignedByte()
        self.setOpDesc("ADD", "SP", asmHex(b))
        value = (int(self.sp) + b) % 0x10000
        self.pc += 2
        self.cycles += 4
        self.f.setZero(False)
        self.f.setSubtract(False)
        self.f.setHalfCarry(bool(value & (1 << 12)))
        self.f.setCarry(value != int(self.sp))
        self.sp.set(value)

    # SUB
    def subBase(self, byte):
        value = int(self.a) - byte
        newValue = value % 0x100
        self.a.set(newValue)
        self.f.setZero(value == 0)
        self.f.setSubtract(True)
        self.f.setHalfCarry(self.a.getBit(4)) #TODO: VERIFY
        self.f.setCarry(value != newValue)

    def sub_rr(self, r):
        self.setOpDesc("SUB", "A", r.getName())
        self.subBase(int(r))
        self.pc += 1
        self.cycles += 1

    def sub_rX(self, X):
        self.setOpDesc("SUB", "A", "({})".format(X.getName()))
        self.subBase(self.mem.read(int(X)))
        self.pc += 1
        self.cycles += 2

    def sub_rb(self):
        b = self.getImmediateByte()
        self.setOpDesc("SUB", "A", asmHex(b))
        self.subBase(b)
        self.pc += 2
        self.cycles += 2

    def sbc_rr(self, r):
        self.setOpDesc("SUB", "A", r.getName())
        self.subBase(int(r) - int(self.f.getCarry()))
        self.pc += 1
        self.cycles += 1

    def sbc_rX(self, X):
        self.setOpDesc("SUB", "A", "({})".format(X.getName()))
        self.subBase(self.mem.read(int(X)) - int(self.f.getCarry()))
        self.pc += 1
        self.cycles += 2

    def sbc_rb(self):
        b = self.getImmediateByte()
        self.setOpDesc("SUB", "A", asmHex(b))
        self.subBase(b - int(self.f.getCarry()))
        self.pc += 2
        self.cycles += 2

    # AND
    def bitwiseBase(self):
        self.f.setZero(int(self.a) == 0)
        self.f.setSubtract(False)
        self.f.setHalfCarry(False)
        self.f.setCarry(False)

    def and_r(self, r):
        self.setOpDesc("AND", r.getName())
        value = int(self.a) & int(r)
        self.a.set(value)
        self.pc += 1
        self.cycles += 1
        self.bitwiseBase()

    def and_X(self, X):
        self.setOpDesc("AND", "({})".format(X.getName()))
        value = int(self.a) & self.mem.read(int(X))
        self.a.set(value)
        self.pc += 1
        self.cycles += 2
        self.bitwiseBase()

    def and_b(self):
        b = self.getImmediateByte()
        self.setOpDesc("AND", asmHex(b))
        value = int(self.a) & b
        self.a.set(value)
        self.pc += 2
        self.cycles += 2
        self.bitwiseBase()

    # OR
    def or_r(self, r):
        self.setOpDesc("OR", r.getName())
        value = int(self.a) | int(r)
        self.a.set(value)
        self.pc += 1
        self.cycles += 1
        self.bitwiseBase()

    def or_X(self, X):
        self.setOpDesc("OR", "({})".format(X.getName()))
        value = int(self.a) | self.mem.read(int(X))
        self.a.set(value)
        self.pc += 1
        self.cycles += 2
        self.bitwiseBase()

    def or_b(self):
        b = self.getImmediateByte()
        self.setOpDesc("OR", asmHex(b))
        value = int(self.a) | b
        self.a.set(value)
        self.pc += 2
        self.cycles += 2
        self.bitwiseBase()

    # XOR
    def xor_r(self, r):
        self.setOpDesc("XOR", r.getName())
        xor = int(self.a) ^ int(r)
        self.a.set(xor)
        self.pc += 1
        self.cycles += 1
        self.bitwiseBase()

    def xor_X(self, X):
        self.setOpDesc("XOR", "({})".format(X.getName()))
        xor = int(self.a) ^ self.mem.read(int(X))
        self.a.set(xor)
        self.pc += 1
        self.cycles += 2
        self.bitwiseBase()

    def xor_b(self):
        b = self.getImmediateByte()
        self.setOpDesc("XOR", asmHex(b))
        xor = int(self.a) ^ b
        self.a.set(xor)
        self.pc += 2
        self.cycles += 2
        self.bitwiseBase()

    # INC
    def inc_r(self, r):
        self.setOpDesc("INC", r.getName())
        newValue = (int(r) + 1) % 0x100
        r.set(newValue)
        self.pc += 1
        self.cycles += 1
        self.f.setZero(newValue == 0)
        self.f.setSubtract(False)
        self.f.setHalfCarry(r.getBit(4))

    def inc_X(self):
        self.setOpDesc("INC", "(HL)")
        newValue = (self.mem.read(int(self.hl)) + 1) % 0x100
        self.mem.write(int(self.hl), newValue)
        self.pc += 1
        self.cycles += 3
        self.f.setZero(newValue == 0)
        self.f.setSubtract(False)
        self.f.setHalfCarry(bool(newValue & 0b1000))

    def inc_x(self, x):
        self.setOpDesc("INC", x.getName())
        x += 1
        self.pc += 1
        self.cycles += 2

    # DEC
    def dec_r(self, r):
        self.setOpDesc("DEC", r.getName())
        newValue = (int(r) - 1) % 0x100
        r.set(newValue)
        self.pc += 1
        self.cycles += 1
        self.f.setZero(newValue == 0)
        self.f.setSubtract(True)
        self.f.setHalfCarry(r.getBit(4))

    def dec_X(self):
        self.setOpDesc("DEC", "(HL)")
        newValue = (self.mem.read(int(self.hl)) -1) % 0x100
        self.mem.write(int(self.hl), newValue)
        self.pc += 1
        self.cycles += 3
        self.f.setZero(newValue == 0)
        self.f.setSubtract(True)
        self.f.setHalfCarry(bool(newValue & 0b1000))

    def dec_x(self, x):
        self.setOpDesc("DEC", x.getName())
        x -= 1
        self.pc += 1
        self.cycles += 2

    # Misc ALU
    def daa(self):
        self.setOpDesc("DAA")

        addend = 6
        if self.f.getSubtract():
            addend *= -1

        value = int(self.a)
        if (value & 0x00FF) > 9 or self.f.getHalfCarry():
            value += addend
        if ((value & 0xFF00) >> 4) > 9 or self.f.getCarry():
            value += addend * 10

        modValue = value % 0x100

        self.f.setCarry(value != modValue)
        self.a.set(modValue)
        self.pc += 1
        self.cycles += 1
        self.f.setZero(value == 0)
        self.f.setHalfCarry(False)

    def cpl(self):
        self.setOpDesc("CPL")
        self.a.set(~int(self.a))
        self.pc += 1
        self.cycles += 1
        self.f.setSubtract(True)
        self.f.setHalfCarry(True)

    # Rotates
    def rotateBase(self):
        self.pc += 1
        self.f.setZero(self.a == 0)
        self.f.setSubtract(False)
        self.f.setHalfCarry(False)

    def rlca(self):
        self.setOpDesc("RRCA")
        carry = self.a.getBit(7)
        newValue = ((int(self.a) << 1) | int(carry)) & 0xFF
        self.f.setCarry(carry)
        self.a.set(newValue)
        self.cycles += 1
        self.rotateBase()

    def rrca(self):
        self.setOpDesc("RRCA")
        carry = self.a.getBit(0)
        newValue = (int(self.a) >> 1) | (int(carry) << 7)
        self.f.setCarry(carry)
        self.a.set(newValue)
        self.cycles += 1
        self.rotateBase()

    def rla(self):
        self.setOpDesc("RLA")
        newValue = ((int(self.a) << 1) | int(self.f.getCarry())) & 0xFF
        self.f.setCarry(self.a.getBit(7))
        self.a.set(newValue)
        self.cycles += 1
        self.rotateBase()

    def rra(self):
        self.setOpDesc("RRA")
        newValue = (int(self.a) >> 1) | (int(self.f.getCarry()) << 7)
        self.f.setCarry(self.a.getBit(0))
        self.a.set(newValue)
        self.cycles += 1
        self.rotateBase()

    def rlc_r(self, r):
        self.setOpDesc("RLC", r.getName())
        carry = r.getBit(7)
        newValue = (int(r) << 1) | int(carry) & 0xFF
        self.f.setCarry(carry)
        r.set(newValue)
        self.cycles += 2
        self.rotateBase()

    def rrc_r(self, r):
        self.setOpDesc("RRC", r.getName())
        carry = r.getBit(0)
        newValue = (int(r) >> 1) | (int(carry) << 7)
        self.f.setCarry(carry)
        r.set(newValue)
        self.cycles += 2
        self.rotateBase()

    def rl_r(self, r):
        self.setOpDesc("RL", r.getName())
        newValue = ((int(r) << 1) | int(self.f.getCarry())) & 0xFF
        self.f.setCarry(r.getBit(7))
        r.set(newValue)
        self.cycles += 2
        self.rotateBase()

    def rr_r(self, r):
        self.setOpDesc("RR", r.getName())
        newValue = (int(r) >> 1) | (int(self.f.getCarry()) << 7)
        self.f.setCarry(r.getBit(0))
        r.set(newValue)
        self.cycles += 2
        self.rotateBase()

    def rlc_X(self, X):
        self.setOpDesc("RLC", "({})".format(X.getName()))
        address = int(X)
        value = self.mem.read(address)

        carry = (value & 0b10000000) >> 7
        newValue = ((value << 1) | int(carry)) & 0xFF
        self.f.setCarry(carry)
        self.mem.write(address, value)
        self.cycles += 4
        self.rotateBase()

    def rrc_X(self, X):
        self.setOpDesc("RRC", "({})".format(X.getName()))
        address = int(X)
        value = self.mem.read(address)

        carry = value & 1
        newValue = (value >> 1) | (int(carry) << 7)
        self.f.setCarry(carry)
        self.mem.write(address, newValue)
        self.cycles += 4
        self.rotateBase()

    def rl_X(self, X):
        self.setOpDesc("RRA", "({})".format(X.getName()))
        address = int(X)
        value = self.mem.read(address)

        newValue = ((value << 1) | int(self.f.getCarry())) & 0xFF
        self.f.setCarry((value & 0b10000000) >> 7)
        self.mem.write(address, newValue)
        self.cycles += 4
        self.rotateBase()

    def rr_X(self, X):
        self.setOpDesc("RRA", "({})".format(X.getName()))
        address = int(X)
        value = self.mem.read(address)

        newValue = (value >> 1) | (int(self.f.getCarry()) << 7)
        self.f.setCarry(value & 1)
        self.mem.write(address, newValue)
        self.cycles += 4
        self.rotateBase()

    # Shifts
    def sla_r(self, r):
        self.setOpDesc("SLA", r.getName())
        self.f.setCarry(r.getBit(7))
        r.set((int(r) << 1) & 0xFF)
    
        self.pc += 1
        self.cycles += 2
        self.f.setZero(int(r) == 0)
        self.f.setSubtract(False)
        self.f.setHalfCarry(False)

    def sla_X(self, X):
        self.setOpDesc("SLA", "({})".format(X.getName()))
        location = int(X)
        b = self.mem.read(location)
        self.f.setCarry(bool(b & 0b10000000))
        value = (b << 1) & 0xFF
        self.mem.write(location, value)

        self.pc += 1
        self.cycles += 4
        self.f.setZero(value == 0)
        self.f.setSubtract(False)
        self.f.setHalfCarry(False)

    def sra_r(self, r):
        self.setOpDesc("SRA", r.getName())
        self.f.setCarry(r.getBit(0))
        r.set((int(r) >> 1) | (int(r) & 0b10000000))

        self.pc += 1
        self.cycles += 2
        self.f.setZero(int(r) == 0)
        self.f.setSubtract(False)
        self.f.setHalfCarry(False)

    def sra_X(self, X):
        self.setOpDesc("SRA", "({})".format(X.getName()))
        location = int(X)
        b = self.mem.read(location)
        self.f.setCarry(bool(b & 1))
        value = (b >> 1) | (b & 0b10000000)
        self.mem.write(location, value)

        self.pc += 1
        self.cycles += 4
        self.f.setZero(value == 0)
        self.f.setSubtract(False)
        self.f.setHalfCarry(False)

    def srl_r(self, r):
        self.setOpDesc("SRL", r.getName())
        self.f.setCarry(r.getBit(0))
        r.set(int(r) >> 1)

        self.pc += 1
        self.cycles += 2
        self.f.setZero(int(r) == 0)
        self.f.setSubtract(False)
        self.f.setHalfCarry(False)

    def srl_X(self, X):
        self.setOpDesc("SRL", "({})".format(X.getName()))
        location = int(X)
        b = self.mem.read(location)
        self.f.setCarry(bool(b & 1))
        value = b >> 1
        self.mem.write(location, value)

        self.pc += 1
        self.cycles += 4
        self.f.setZero(value == 0)
        self.f.setSubtract(False)
        self.f.setHalfCarry(False)

    # Set Bit
    def set_ir(self, i, r):
        self.setOpDesc("SET", str(i), r.getName())
        r.setBit(i, True)

        self.pc += 1
        self.cycles += 2

    def set_iX(self, i, X):
        self.setOpDesc("SET", str(i), "({})".format(X.getName()))
        address = int(X)
        value = self.mem.read(address)
        value |= (1 << i)
        self.mem.write(address, value)

        self.pc += 1
        self.cycles += 4

    # Reset Bit
    def res_ir(self, i, r):
        self.setOpDesc("RES", str(i), r.getName())
        r.setBit(i, False)

        self.pc += 1
        self.cycles += 2

    def res_iX(self, i, X):
        self.setOpDesc("RES", str(i), "({})".format(X.getName()))
        address = int(X)
        value = self.mem.read(address)
        value &= ~(1 << i)
        self.mem.write(address, value)

        self.pc += 1
        self.cycles += 4

    # Get Bit
    def bit_ir(self, i, r):
        self.setOpDesc("BIT", str(i), r.getName())

        self.pc += 1
        self.cycles += 2
        self.f.setZero(r.getBit(i))
        self.f.setSubtract(0)
        self.f.setHalfCarry(1)

    def bit_iX(self, i, X):
        self.setOpDesc("BIT", str(i), "({})".format(X.getName()))
        address = int(X)
        value = self.mem.read(address)
        bit = bool(value & (1 << i))

        self.pc += 1
        self.cycles += 4
        self.f.setZero(bit)
        self.f.setSubtract(0)
        self.f.setHalfCarry(1)

    # Swap
    def swap_r(self, r):
        self.setOpDesc("SWAP", "{}".format(r.getName()))
        value = int(r)
        newValue = ((value & 0xF0) >> 4) & ((value & 0x0F) << 4)
        r.set(newValue)

        self.f.setZero(newValue == 0)
        self.f.setSubtract(0)
        self.f.setHalfCarry(0)
        self.f.setCarry(0)
        self.pc += 1
        self.cycles += 2

    def swap_X(self):
        self.setOpDesc("SWAP", "(HL)")
        address = int(self.hl)
        value = self.mem.read(address)
        newValue = ((value & 0xF0) >> 4) & ((value & 0x0F) << 4)
        self.mem.write(address, newValue)

        self.f.setZero(newValue == 0)
        self.f.setSubtract(0)
        self.f.setHalfCarry(0)
        self.f.setCarry(0)
        self.pc += 1
        self.cycles += 4

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# Chuck this in another file
def asmHex(integer, width = 2):
    if integer >= 0:
        return "$" + hex(integer)[2:].zfill(width)
    else:
        return "-$" + hex(integer)[3:].zfill(width)
