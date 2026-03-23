from amaranth import *
from amaranth.hdl import *
from enum import IntEnum


class ImmType(IntEnum):
    I = 0
    S = 1
    B = 2
    U = 3
    J = 4

class ImmGen(Elaboratable):
    """Generador de inmediatos para instrucciones RISC-V."""
    
    def __init__(self):
        # Entradas
        self.instruction = Signal(32, name="instruction")  # Instrucción de 32 bits
        self.imm_type = Signal(3, name="imm_type")        # Tipo de inmediato (3 bits)

        # Salidas
        self.imm = Signal(32, name="imm")  # Inmediato generado (32 bits)
    
    def elaborate(self, platform):
        m = Module()
        sign = self.instruction[31]

        sign_fill20 = Mux(sign, Const((1 << 20) - 1, 20), Const(0, 20))
        sign_fill19 = Mux(sign, Const((1 << 19) - 1, 19), Const(0, 19))
        sign_fill11 = Mux(sign, Const((1 << 11) - 1, 11), Const(0, 11))

        # Valor por defecto seguro.
        m.d.comb += self.imm.eq(0)

        # Generación de inmediato según el tipo especificado.
        with m.Switch(self.imm_type):
            with m.Case(ImmType.I):  # I-type (instr[31:20], sign-extend)
                m.d.comb += self.imm.eq(Cat(self.instruction[20:32], sign_fill20))
            with m.Case(ImmType.S):  # S-type (instr[31:25|11:7], sign-extend)
                m.d.comb += self.imm.eq(Cat(self.instruction[7:12], self.instruction[25:32], sign_fill20))
            with m.Case(ImmType.B):  # B-type (offset de branch, bit0 = 0)
                m.d.comb += self.imm.eq(Cat(
                    C(0, 1),                      # imm[0]
                    self.instruction[8:12],       # imm[4:1]
                    self.instruction[25:31],      # imm[10:5]
                    self.instruction[7],          # imm[11]
                    self.instruction[31],         # imm[12]
                    sign_fill19
                ))
            with m.Case(ImmType.U):  # U-type (instr[31:12] << 12)
                m.d.comb += self.imm.eq(Cat(C(0, 12), self.instruction[12:32]))
            with m.Case(ImmType.J):  # J-type (offset de jump, bit0 = 0)
                m.d.comb += self.imm.eq(Cat(
                    C(0, 1),                      # imm[0]
                    self.instruction[21:31],      # imm[10:1]
                    self.instruction[20],         # imm[11]
                    self.instruction[12:20],      # imm[19:12]
                    self.instruction[31],         # imm[20]
                    sign_fill11
                ))
        return m
