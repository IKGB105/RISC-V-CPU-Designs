from amaranth import *
from amaranth.hdl import *
from enum import IntEnum

#Para que se pueda entender mejor el codigo se agregan nombres a las operaciones de la ALU, en vez de usar numeros magicos. Esto hace que el codigo sea mas legible y facil de mantener.
class ALUOp(IntEnum):
    AND = 0
    OR = 1
    XOR = 2
    SLL = 3
    SRL = 4
    SRA = 5
    SLT = 6
    SLTU = 7
    ADD = 8
    SUB = 9

class ALU(Elaboratable):
    """Unidad de Operaciones Aritméticas y Lógicas"""
    
    def __init__(self):
        # Puertos
        self.a = Signal(32, name="a")      # Entrada A (32 bits)
        self.b = Signal(32, name="b")      # Entrada B (32 bits)
        self.alu_operation = Signal(4, name="alu_operation")  # Operación ALU (4 bits)
        self.result = Signal(32, name="result")  # Resultado (32 bits)
        self.zero = Signal(name="zero")    # Flag de resultado cero
        self.lt = Signal(name="lt")      # Flag de resultado menor que cero
        self.ltu = Signal(name="ltu")    # Flag de resultado menor que cero (unsigned)
    
    def elaborate(self, platform):
        m = Module()
        
        # Resultado por defecto.
        m.d.comb += self.result.eq(0)

        # Selección de operación ALU con etiquetas legibles (ALUOp.*)
        with m.Switch(self.alu_operation):
            with m.Case(ALUOp.AND):
                m.d.comb += self.result.eq(self.a & self.b) # AND bit a bit
            with m.Case(ALUOp.OR):
                m.d.comb += self.result.eq(self.a | self.b) # OR bit a bit
            with m.Case(ALUOp.XOR):
                m.d.comb += self.result.eq(self.a ^ self.b) # XOR bit a bit
            with m.Case(ALUOp.SLL):
                m.d.comb += self.result.eq(self.a << self.b[0:5])  # Shift left logical
            with m.Case(ALUOp.SRL):
                m.d.comb += self.result.eq(self.a >> self.b[0:5])  # Shift right logical
            with m.Case(ALUOp.SRA):
                m.d.comb += self.result.eq(self.a.as_signed() >> self.b[0:5])  # Shift right arithmetic
            with m.Case(ALUOp.SLT):
                m.d.comb += self.result.eq((self.a.as_signed() < self.b.as_signed()).as_unsigned())  # Set less than (signed)
            with m.Case(ALUOp.SLTU):
                m.d.comb += self.result.eq((self.a < self.b).as_unsigned())  # Set less than (unsigned)
            with m.Case(ALUOp.ADD):
                m.d.comb += self.result.eq(self.a + self.b)  # Add
            with m.Case(ALUOp.SUB):
                m.d.comb += self.result.eq(self.a - self.b)  # Subtract

        # Flags de comparación útiles para branches.
        m.d.comb += [
            self.zero.eq(self.result == 0),
            self.lt.eq(self.a.as_signed() < self.b.as_signed()),
            self.ltu.eq(self.a < self.b),
        ]
        
        return m
