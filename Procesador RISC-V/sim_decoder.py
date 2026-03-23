from amaranth.sim import Simulator, Delay

from ALU import ALUOp
from Decoder import Decoder, ImmType, WBSel


if __name__ == "__main__":
    dut = Decoder()
    sim = Simulator(dut)

    tests = [
        # name, instr, expected dict
        (
            "ADD",
            (0x00 << 25) | (3 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0x33,
            {
                "alu_op": int(ALUOp.ADD),
                "reg_we": 1,
                "alu_src_imm": 0,
                "mem_re": 0,
                "mem_we": 0,
                "branch": 0,
                "jump": 0,
                "jalr": 0,
                "wb_sel": int(WBSel.ALU),
                "imm_type": int(ImmType.I),
            },
        ),
        (
            "SUB",
            (0x20 << 25) | (3 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0x33,
            {
                "alu_op": int(ALUOp.SUB),
                "reg_we": 1,
                "alu_src_imm": 0,
                "wb_sel": int(WBSel.ALU),
            },
        ),
        (
            "ADDI",
            (5 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0x13,
            {
                "alu_op": int(ALUOp.ADD),
                "reg_we": 1,
                "alu_src_imm": 1,
                "wb_sel": int(WBSel.ALU),
                "imm_type": int(ImmType.I),
            },
        ),
        (
            "LW",
            (8 << 20) | (2 << 15) | (0b010 << 12) | (1 << 7) | 0x03,
            {
                "alu_op": int(ALUOp.ADD),
                "reg_we": 1,
                "alu_src_imm": 1,
                "mem_re": 1,
                "mem_we": 0,
                "wb_sel": int(WBSel.MEM),
                "imm_type": int(ImmType.I),
            },
        ),
        (
            "SW",
            (1 << 25) | (5 << 20) | (2 << 15) | (0b010 << 12) | (0 << 7) | 0x23,
            {
                "alu_op": int(ALUOp.ADD),
                "reg_we": 0,
                "alu_src_imm": 1,
                "mem_re": 0,
                "mem_we": 1,
                "imm_type": int(ImmType.S),
            },
        ),
        (
            "BEQ",
            (0 << 31) | (0 << 7) | (0 << 25) | (3 << 20) | (2 << 15) | (0b000 << 12) | 0x63,
            {
                "branch": 1,
                "imm_type": int(ImmType.B),
                "reg_we": 0,
            },
        ),
        (
            "JAL",
            (1 << 7) | 0x6F,
            {
                "jump": 1,
                "reg_we": 1,
                "wb_sel": int(WBSel.PC4),
                "imm_type": int(ImmType.J),
            },
        ),
        (
            "JALR",
            (4 << 20) | (2 << 15) | (0b000 << 12) | (1 << 7) | 0x67,
            {
                "jalr": 1,
                "reg_we": 1,
                "alu_src_imm": 1,
                "wb_sel": int(WBSel.PC4),
                "imm_type": int(ImmType.I),
            },
        ),
        (
            "LUI",
            (0x12345 << 12) | (1 << 7) | 0x37,
            {
                "reg_we": 1,
                "wb_sel": int(WBSel.IMM),
                "imm_type": int(ImmType.U),
            },
        ),
        (
            "AUIPC",
            (0x12345 << 12) | (1 << 7) | 0x17,
            {
                "reg_we": 1,
                "alu_src_imm": 1,
                "wb_sel": int(WBSel.ALU),
                "imm_type": int(ImmType.U),
                "alu_op": int(ALUOp.ADD),
            },
        ),
    ]

    signal_map = {
        "alu_op": dut.alu_op,
        "reg_we": dut.reg_we,
        "alu_src_imm": dut.alu_src_imm,
        "mem_re": dut.mem_re,
        "mem_we": dut.mem_we,
        "branch": dut.branch,
        "jump": dut.jump,
        "jalr": dut.jalr,
        "wb_sel": dut.wb_sel,
        "imm_type": dut.imm_type,
    }

    def process():
        ok = 0
        total = 0

        for name, instr, expected in tests:
            yield dut.instruction.eq(instr)
            yield Delay(1e-9)

            local_ok = True
            for key, exp in expected.items():
                got = (yield signal_map[key])
                total += 1
                if got == exp:
                    ok += 1
                else:
                    local_ok = False
                    print(f"{name} {key}: got={got} exp={exp} FAIL")

            if local_ok:
                print(f"{name}: PASS")

        print(f"\nResumen: {ok}/{total} checks OK")

    sim.add_process(process)

    with sim.write_vcd(
        "decoder.vcd",
        "decoder.gtkw",
        traces=[
            dut.instruction,
            dut.opcode,
            dut.rd,
            dut.funct3,
            dut.rs1,
            dut.rs2,
            dut.funct7,
            dut.alu_op,
            dut.reg_we,
            dut.alu_src_imm,
            dut.mem_re,
            dut.mem_we,
            dut.branch,
            dut.jump,
            dut.jalr,
            dut.wb_sel,
            dut.imm_type,
        ],
    ):
        sim.run()

    print("Archivos generados: decoder.vcd y decoder.gtkw")
