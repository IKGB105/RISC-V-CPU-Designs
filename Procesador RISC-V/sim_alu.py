from amaranth.sim import Simulator, Delay

from ALU import ALU, ALUOp


def u32(x: int) -> int:
    return x & 0xFFFFFFFF


def s32(x: int) -> int:
    x &= 0xFFFFFFFF
    return x if x < 0x80000000 else x - 0x100000000


def expected_result(op: int, a: int, b: int) -> int:
    a_u = u32(a)
    b_u = u32(b)
    shamt = b_u & 0x1F

    if op == ALUOp.AND:
        return u32(a_u & b_u)
    if op == ALUOp.OR:
        return u32(a_u | b_u)
    if op == ALUOp.XOR:
        return u32(a_u ^ b_u)
    if op == ALUOp.SLL:
        return u32(a_u << shamt)
    if op == ALUOp.SRL:
        return u32(a_u >> shamt)
    if op == ALUOp.SRA:
        return u32(s32(a_u) >> shamt)
    if op == ALUOp.SLT:
        return 1 if s32(a_u) < s32(b_u) else 0
    if op == ALUOp.SLTU:
        return 1 if a_u < b_u else 0
    if op == ALUOp.ADD:
        return u32(a_u + b_u)
    if op == ALUOp.SUB:
        return u32(a_u - b_u)

    return 0


if __name__ == "__main__":
    dut = ALU()
    sim = Simulator(dut)

    # Casos para cubrir todas las operaciones y bordes de signed/unsigned.
    tests = [
        (ALUOp.AND, 0xF0F0F0F0, 0x0FF00FF0),
        (ALUOp.OR, 0x12340000, 0x00005678),
        (ALUOp.XOR, 0xAAAAAAAA, 0x55555555),
        (ALUOp.SLL, 0x00000001, 4),
        (ALUOp.SRL, 0x80000000, 4),
        (ALUOp.SRA, 0x80000000, 4),
        (ALUOp.SLT, 0xFFFFFFFF, 0x00000001),  # -1 < 1 => 1
        (ALUOp.SLTU, 0xFFFFFFFF, 0x00000001), # 4294967295 < 1 => 0
        (ALUOp.SLT, 0x00000005, 0x00000008),
        (ALUOp.SLTU, 0x00000005, 0x00000008),
        (ALUOp.ADD, 0x00000005, 0x00000008),
        (ALUOp.ADD, 0xFFFFFFFF, 0x00000001),  # overflow natural de 32 bits -> 0
        (ALUOp.SUB, 0x00000008, 0x00000005),
        (ALUOp.SUB, 0x00000000, 0x00000001),  # wrap-around -> 0xFFFFFFFF
    ]

    def process():
        ok = 0
        for i, (op, a, b) in enumerate(tests):
            exp = expected_result(op, a, b)

            yield dut.alu_operation.eq(int(op))
            yield dut.a.eq(u32(a))
            yield dut.b.eq(u32(b))

            # Da tiempo a que la lógica combinacional se propague.
            yield Delay(1e-9)

            got = (yield dut.result)
            zero = (yield dut.zero)
            lt = (yield dut.lt)
            ltu = (yield dut.ltu)

            passed = got == exp
            ok += 1 if passed else 0

            print(
                f"[{i:02d}] op={op.name:<4} "
                f"a=0x{u32(a):08X} b=0x{u32(b):08X} "
                f"got=0x{got:08X} exp=0x{exp:08X} "
                f"zero={zero} lt={lt} ltu={ltu} {'PASS' if passed else 'FAIL'}"
            )

        print(f"\nResumen: {ok}/{len(tests)} pruebas OK")

    sim.add_process(process)

    with sim.write_vcd(
        "alu.vcd",
        "alu.gtkw",
        traces=[dut.alu_operation, dut.a, dut.b, dut.result, dut.zero, dut.lt, dut.ltu],
    ):
        sim.run()

    print("Archivos generados: alu.vcd y alu.gtkw")
