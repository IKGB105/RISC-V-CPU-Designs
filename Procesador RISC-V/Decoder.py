from amaranth import *
from amaranth.hdl import *
from enum import IntEnum

from ALU import ALUOp

class WBSel(IntEnum):
    ALU = 0
    MEM = 1
    PC4 = 2
    IMM = 3


class ImmType(IntEnum):
    I = 0
    S = 1
    B = 2
    U = 3
    J = 4


class Decoder(Elaboratable):
    """Decoder for RISC-V instruction set."""
    
    def __init__(self):
        # Entradas
        self.instruction = Signal(32, name="instruction")  # Instrucción de 32 bits

        # Salidas 
        self.opcode = Signal(7, name="opcode")          # Código de operación (7 bits)
        self.rd = Signal(5, name="rd")                  # Registro destino (5 bits)
        self.funct3 = Signal(3, name="funct3")          # Función 3 (3 bits)
        self.rs1 = Signal(5, name="rs1")                # Registro fuente 1 (5 bits)
        self.rs2 = Signal(5, name="rs2")                # Registro fuente 2 (5 bits)
        self.funct7 = Signal(7, name="funct7")          # Función 7 (7 bits)

        # Señales de control
        self.alu_op = Signal(4, name="alu_op")
        self.reg_we = Signal(name="reg_we")
        self.alu_src_imm = Signal(name="alu_src_imm")
        self.mem_re = Signal(name="mem_re")
        self.mem_we = Signal(name="mem_we")
        self.branch = Signal(name="branch")
        self.jump = Signal(name="jump")
        self.jalr = Signal(name="jalr")
        self.wb_sel = Signal(2, name="wb_sel")
        self.imm_type = Signal(3, name="imm_type")

    def elaborate(self, platform):
        m = Module()

        # Decodificación de campos fijos de la instrucción RISC-V.
        m.d.comb += [
            self.opcode.eq(self.instruction[0:7]),    # bits [6:0]
            self.rd.eq(self.instruction[7:12]),       # bits [11:7]
            self.funct3.eq(self.instruction[12:15]),  # bits [14:12]
            self.rs1.eq(self.instruction[15:20]),     # bits [19:15]
            self.rs2.eq(self.instruction[20:25]),     # bits [24:20]
            self.funct7.eq(self.instruction[25:32]),  # bits [31:25]
        ]

        # Defaults de control (NOP seguro) para evitar valores colgados.
        m.d.comb += [
            self.alu_op.eq(ALUOp.ADD),
            self.reg_we.eq(0),
            self.alu_src_imm.eq(0),
            self.mem_re.eq(0),
            self.mem_we.eq(0),
            self.branch.eq(0),
            self.jump.eq(0),
            self.jalr.eq(0),
            self.wb_sel.eq(WBSel.ALU),
            self.imm_type.eq(ImmType.I),
        ]

        # Decode principal por opcode.
        with m.Switch(self.opcode):
            # R-type: OP (ADD, SUB, AND, OR, XOR, SLL, SRL, SRA, SLT, SLTU)
            with m.Case(0x33):
                m.d.comb += [
                    self.reg_we.eq(1),
                    self.alu_src_imm.eq(0),
                    self.wb_sel.eq(WBSel.ALU),
                ]

                with m.Switch(self.funct3):
                    with m.Case(0b000):
                        with m.If(self.funct7 == 0b0100000):
                            m.d.comb += self.alu_op.eq(ALUOp.SUB)
                        with m.Else():
                            m.d.comb += self.alu_op.eq(ALUOp.ADD)
                    with m.Case(0b111):
                        m.d.comb += self.alu_op.eq(ALUOp.AND)
                    with m.Case(0b110):
                        m.d.comb += self.alu_op.eq(ALUOp.OR)
                    with m.Case(0b100):
                        m.d.comb += self.alu_op.eq(ALUOp.XOR)
                    with m.Case(0b001):
                        m.d.comb += self.alu_op.eq(ALUOp.SLL)
                    with m.Case(0b101):
                        with m.If(self.funct7 == 0b0100000):
                            m.d.comb += self.alu_op.eq(ALUOp.SRA)
                        with m.Else():
                            m.d.comb += self.alu_op.eq(ALUOp.SRL)
                    with m.Case(0b010):
                        m.d.comb += self.alu_op.eq(ALUOp.SLT)
                    with m.Case(0b011):
                        m.d.comb += self.alu_op.eq(ALUOp.SLTU)

            # I-type ALU immediates: OP-IMM
            with m.Case(0x13):
                m.d.comb += [
                    self.reg_we.eq(1),
                    self.alu_src_imm.eq(1),
                    self.wb_sel.eq(WBSel.ALU),
                    self.imm_type.eq(ImmType.I),
                ]

                with m.Switch(self.funct3):
                    with m.Case(0b000):
                        m.d.comb += self.alu_op.eq(ALUOp.ADD)   # ADDI
                    with m.Case(0b111):
                        m.d.comb += self.alu_op.eq(ALUOp.AND)   # ANDI
                    with m.Case(0b110):
                        m.d.comb += self.alu_op.eq(ALUOp.OR)    # ORI
                    with m.Case(0b100):
                        m.d.comb += self.alu_op.eq(ALUOp.XOR)   # XORI
                    with m.Case(0b001):
                        m.d.comb += self.alu_op.eq(ALUOp.SLL)   # SLLI
                    with m.Case(0b101):
                        with m.If(self.funct7 == 0b0100000):
                            m.d.comb += self.alu_op.eq(ALUOp.SRA)  # SRAI
                        with m.Else():
                            m.d.comb += self.alu_op.eq(ALUOp.SRL)  # SRLI
                    with m.Case(0b010):
                        m.d.comb += self.alu_op.eq(ALUOp.SLT)   # SLTI
                    with m.Case(0b011):
                        m.d.comb += self.alu_op.eq(ALUOp.SLTU)  # SLTIU

            # LOAD
            with m.Case(0x03):
                m.d.comb += [
                    self.reg_we.eq(1),
                    self.alu_src_imm.eq(1),
                    self.mem_re.eq(1),
                    self.wb_sel.eq(WBSel.MEM),
                    self.imm_type.eq(ImmType.I),
                    self.alu_op.eq(ALUOp.ADD),  # dirección = rs1 + imm
                ]

            # STORE
            with m.Case(0x23):
                m.d.comb += [
                    self.alu_src_imm.eq(1),
                    self.mem_we.eq(1),
                    self.imm_type.eq(ImmType.S),
                    self.alu_op.eq(ALUOp.ADD),  # dirección = rs1 + imm
                ]

            # BRANCH
            with m.Case(0x63):
                m.d.comb += [
                    self.branch.eq(1),
                    self.imm_type.eq(ImmType.B),
                ]

            # JAL
            with m.Case(0x6F):
                m.d.comb += [
                    self.jump.eq(1),
                    self.reg_we.eq(1),
                    self.wb_sel.eq(WBSel.PC4),
                    self.imm_type.eq(ImmType.J),
                ]

            # JALR
            with m.Case(0x67):
                m.d.comb += [
                    self.jalr.eq(1),
                    self.reg_we.eq(1),
                    self.alu_src_imm.eq(1),
                    self.wb_sel.eq(WBSel.PC4),
                    self.imm_type.eq(ImmType.I),
                    self.alu_op.eq(ALUOp.ADD),
                ]

            # LUI
            with m.Case(0x37):
                m.d.comb += [
                    self.reg_we.eq(1),
                    self.wb_sel.eq(WBSel.IMM),
                    self.imm_type.eq(ImmType.U),
                ]

            # AUIPC
            with m.Case(0x17):
                m.d.comb += [
                    self.reg_we.eq(1),
                    self.alu_src_imm.eq(1),
                    self.wb_sel.eq(WBSel.ALU),
                    self.imm_type.eq(ImmType.U),
                    self.alu_op.eq(ALUOp.ADD),
                ]

        return m
