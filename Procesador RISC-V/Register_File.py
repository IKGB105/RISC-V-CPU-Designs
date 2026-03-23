from amaranth import *
from amaranth.hdl import *


class RegisterFile(Elaboratable):
    """Banco de registros con 32 registros de 32 bits cada uno. El registro x0 siempre lee como 0 y no se puede escribir."""
    
    def __init__(self):
        # Entradas
        self.rs1_address = Signal(5, name="rs1_address")      # Dirección del registro rs1
        self.rs2_address = Signal(5, name="rs2_address")      # Dirección del registro rs2
        self.rd_address = Signal(5, name="rd_address")      # Dirección del registro de escritura
        self.rd_data = Signal(32, name="rd_data")          # Datos a escribir en rd
        self.rd_we = Signal(name="rd_we")               # Señal de escritura en el registro

        # Salidas 
        self.rs1_data = Signal(32, name="rs1_data")          # Datos leídos de rs1
        self.rs2_data = Signal(32, name="rs2_data")          # Datos leídos de rs2

    def elaborate(self, platform):
        m = Module()

        # Banco de registros: 32 registros de 32 bits cada uno.
        registros = Array([Signal(32, name=f"x{i}") for i in range(32)])

        # Lectura de registros rs1 y rs2 (combinacional)
        m.d.comb += [
            # x0 siempre lee como 0.
            self.rs1_data.eq(Mux(self.rs1_address == 0, 0,
                                 Mux(self.rd_we & (self.rd_address != 0) & (self.rd_address == self.rs1_address),
                                     self.rd_data,
                                     registros[self.rs1_address]))),
            self.rs2_data.eq(Mux(self.rs2_address == 0, 0,
                                 Mux(self.rd_we & (self.rd_address != 0) & (self.rd_address == self.rs2_address),
                                     self.rd_data,
                                     registros[self.rs2_address]))),
        ]

        # Escritura en el registro rd (sincrónica)
        with m.If(self.rd_we & (self.rd_address != 0)):  # El registro x0 no se puede escribir
            m.d.sync += registros[self.rd_address].eq(self.rd_data)
        
        
        return m
