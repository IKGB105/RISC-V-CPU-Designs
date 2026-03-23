# RISC-V CPU Designs

two different approaches to understanding RISC-V architecture: python simulation + verilog hardware

## why this repo exists

i got obsessed with understanding how CPUs actually work. not just reading about it — actually building them from scratch. so i did it twice: once in python (to understand the logic), then in verilog (to see it synthesize on real hardware).

## what's inside

### 1. Python/Amaranth Simulator (`Procesador RISC-V/`)

this is the "learning" version. builds the entire RISC-V ISA from the ground up:

**core modules:**
- `Decoder.py` — ISA instruction decoder (extracts opcode, rd, funct3, rs1, rs2, funct7)
- `ALU.py` — 16+ operations (ADD, SUB, MUL, DIV, MULH, MULHU, AND, OR, XOR, SLL, SRL, SRA, etc)
- `Register_File.py` — 32×32 bit register file with dual-port read, single-port write (follows RISC-V spec: x0 always 0)
- `BranchUnit.py` — branch prediction + target calculation
- `ImmGen.py` — immediate value extraction for different instruction types

**simulators:**
- `sim_decoder.py` — test the instruction decoder
- `sim_alu.py` — test ALU operations exhaustively
- `sim_register_file.py` — validate register file behavior

**outputs:**
- VCD files for GTKWave visualization (`decoder.vcd`, `alu.vcd`, `regfile.vcd`)
- waveform configs (`decoder.gtkw`, `alu.gtkw`, `regfile.gtkw`)

**why python?**
because i needed to verify the logic before committing to verilog. python lets you test ideas fast. once the architecture made sense, i moved to hardware.

### 2. Verilog Hardware Design (`Verilog Procesador/`)

this is the "real" version. synthesizable, tested, ready for FPGA:

**modules:**
- `ALU.v` — 32-bit ALU, same operations as python version but in hardware
- `RegisterFile.v` — 32×32 register file for FPGA
- `tb_ALU.v` — exhaustive testbench (20+ test vectors)
- `tb_RegisterFile.v` — register file validation

**test results:**
- `ALU_test.vcd` — captured waveforms from test runs
- `sim_ALU`, `sim_alu_check`, `sim_sumador` — compiled simulations

**synthesis:**
- tested on Xilinx Spartan-6 (Mimas board)
- timing closure achieved
- resource utilization optimized

## how to use this

### python version (simulation)

```bash
cd "Procesador RISC-V"
python3 sim_decoder.py      # test ISA decoder
python3 sim_alu.py          # test ALU operations
python3 sim_register_file.py # test register file
```

outputs go to `.vcd` files. view them:

```bash
gtkwave decoder.vcd &
gtkwave alu.vcd &
gtkwave regfile.vcd &
```

### verilog version (simulation)

```bash
cd "Verilog Procesador"
iverilog -o sim_alu tb_ALU.v ALU.v
vvp sim_alu
gtkwave ALU_test.vcd &
```

### synthesis (xilinx)

```bash
cd "Verilog Procesador"
# open with Xilinx ISE or Vivado
# add ALU.v and RegisterFile.v to project
# run synthesis, P&R, generate bitstream
```

## what i learned

- **instruction decoding is the bottleneck** — getting opcode extraction right took longer than the ALU
- **dual-port reads are tricky in hardware** — synchronization issues between read/write ports
- **python → verilog translation isn't straightforward** — timing constraints change everything
- **testbenches are mandatory** — i found bugs in the verilog that python hid
- **GTKWave is your friend** — seeing waveforms beats reading logs by 100x

## architecture notes

### ISA Support
- RV32I base integer instruction set
- multiplication extension (RV32M): MUL, MULH, MULHU, MULHSU
- division: DIV, DIVU
- bitwise: AND, OR, XOR, NOT, SLL, SRL, SRA
- load/store (basic addressing)
- branches (BEQ, BNE, BLT, BGE, BLTU, BGEU)
- jumps (JAL, JALR)

### Design Decisions
1. **Python for simulation first** — validate architecture logic before synthesis
2. **VCD output for both** — enables waveform debugging at any stage
3. **Exhaustive testing** — 20+ test vectors for ALU, full register file coverage
4. **Register file dual-port optimization** — read happens combinatorial, write is sequential

## file structure

```
├── Procesador RISC-V/              # Python/Amaranth simulator
│   ├── ALU.py                      # ALU implementation
│   ├── Decoder.py                  # ISA decoder
│   ├── Register_File.py            # Register file
│   ├── BranchUnit.py               # Branch logic
│   ├── ImmGen.py                   # Immediate generation
│   ├── sim_alu.py                  # ALU test
│   ├── sim_decoder.py              # Decoder test
│   ├── sim_register_file.py        # Register file test
│   ├── *.vcd                        # Output waveforms
│   └── *.gtkw                       # GTKWave configs
│
└── Verilog Procesador/             # Verilog hardware
    ├── ALU.v                        # ALU module
    ├── RegisterFile.v              # Register file module
    ├── tb_ALU.v                     # ALU testbench
    ├── tb_RegisterFile.v            # RegisterFile testbench
    ├── ALU_test.vcd                 # Simulation output
    └── sim_*                        # Compiled simulations
```

## why two versions?

**simulation version** lets me think about the problem without worrying about synthesis constraints.

**verilog version** forces me to deal with real hardware constraints: timing, area, power.

together they give you both understanding and implementation.

## next steps

- [ ] add pipeline stages (multi-cycle execution)
- [ ] implement cache (L1 I-cache, D-cache)
- [ ] add branch prediction (simple bimodal predictor)
- [ ] optimization for Gowin FPGA (Tang Nano 1K)
- [ ] performance metrics (CPI, IPC)

## testing methodology

each module has its own simulator:
1. unit tests (single module)
2. integration tests (decoder → ALU → RegisterFile chain)
3. waveform validation (GTKWave inspection)
4. synthesis verification (post-P&R simulation)

## disclaimers

- this is **educational code** — i wrote it to learn, not for production
- the python version prioritizes clarity over performance
- the verilog version is optimized for Xilinx Spartan-6 (adjust for your FPGA)
- lots of comments explaining **why** not just **what**
---

⭐ if this helped you understand RISC-V or CPU design, star it. it means someone besides me found it useful.

happy hacking 🚀
