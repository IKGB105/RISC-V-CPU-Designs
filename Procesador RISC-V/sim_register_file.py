from amaranth.sim import Simulator, Tick, Delay

from Register_File import RegisterFile


def u32(x: int) -> int:
    return x & 0xFFFFFFFF


if __name__ == "__main__":
    dut = RegisterFile()
    sim = Simulator(dut)
    sim.add_clock(1e-6)

    def process():
        ok = 0
        total = 0

        # Helper para comparar resultados.
        def check(name: str, got: int, exp: int):
            nonlocal ok, total
            total += 1
            passed = got == exp
            ok += 1 if passed else 0
            print(f"{name}: got=0x{got:08X} exp=0x{exp:08X} {'PASS' if passed else 'FAIL'}")

        # Estado inicial: leer x0 y x1 (deben ser 0)
        yield dut.rs1_address.eq(0)
        yield dut.rs2_address.eq(1)
        yield dut.rd_we.eq(0)
        yield Delay(1e-9)
        check("init rs1(x0)", (yield dut.rs1_data), 0)
        check("init rs2(x1)", (yield dut.rs2_data), 0)

        # Escribir x1 = 0x12345678
        yield dut.rd_address.eq(1)
        yield dut.rd_data.eq(0x12345678)
        yield dut.rd_we.eq(1)
        yield Tick()
        yield dut.rd_we.eq(0)

        yield dut.rs1_address.eq(1)
        yield Delay(1e-9)
        check("read x1", (yield dut.rs1_data), 0x12345678)

        # Intentar escribir x0 (debe ignorarse)
        yield dut.rd_address.eq(0)
        yield dut.rd_data.eq(0xFFFFFFFF)
        yield dut.rd_we.eq(1)
        yield Tick()
        yield dut.rd_we.eq(0)

        yield dut.rs1_address.eq(0)
        yield Delay(1e-9)
        check("write x0 ignored", (yield dut.rs1_data), 0)

        # Sobrescribir x1
        yield dut.rd_address.eq(1)
        yield dut.rd_data.eq(0xDEADBEEF)
        yield dut.rd_we.eq(1)
        yield Tick()
        yield dut.rd_we.eq(0)

        yield dut.rs1_address.eq(1)
        yield Delay(1e-9)
        check("overwrite x1", (yield dut.rs1_data), u32(0xDEADBEEF))

        # Probar rd_we=0 no cambia x1
        yield dut.rd_address.eq(1)
        yield dut.rd_data.eq(0xCAFEBABE)
        yield dut.rd_we.eq(0)
        yield Tick()

        yield dut.rs1_address.eq(1)
        yield Delay(1e-9)
        check("rd_we=0 no write", (yield dut.rs1_data), u32(0xDEADBEEF))

        # Probar x31
        yield dut.rd_address.eq(31)
        yield dut.rd_data.eq(0x0BADF00D)
        yield dut.rd_we.eq(1)
        yield Tick()
        yield dut.rd_we.eq(0)

        yield dut.rs1_address.eq(31)
        yield Delay(1e-9)
        check("write/read x31", (yield dut.rs1_data), 0x0BADF00D)

        # Probar bypass (lectura y escritura mismo ciclo)
        yield dut.rs1_address.eq(5)
        yield dut.rs2_address.eq(5)
        yield dut.rd_address.eq(5)
        yield dut.rd_data.eq(0x11223344)
        yield dut.rd_we.eq(1)
        yield Delay(1e-9)
        check("bypass rs1", (yield dut.rs1_data), 0x11223344)
        check("bypass rs2", (yield dut.rs2_data), 0x11223344)

        print(f"\nResumen: {ok}/{total} pruebas OK")

    sim.add_process(process)

    with sim.write_vcd(
        "regfile.vcd",
        "regfile.gtkw",
        traces=[
            dut.rs1_address,
            dut.rs2_address,
            dut.rd_address,
            dut.rd_data,
            dut.rd_we,
            dut.rs1_data,
            dut.rs2_data,
        ],
    ):
        sim.run()

    print("Archivos generados: regfile.vcd y regfile.gtkw")
