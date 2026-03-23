// ================================================================
// SystemVerilog básico (guía rápida para alguien que ya sabe VHDL)
// Archivo de referencia: declaraciones, tipos y bloques más usados.
// ================================================================

`timescale 1ns/1ps

// ----------------------------------------------------------------
// 1) PACKAGE: parecido a package en VHDL
// ----------------------------------------------------------------
package cpu_types_pkg;

  // Equivalente a un enum de VHDL
  typedef enum logic [2:0] {
    ALU_ADD  = 3'd0,
    ALU_SUB  = 3'd1,
    ALU_AND  = 3'd2,
    ALU_OR   = 3'd3,
    ALU_XOR  = 3'd4,
    ALU_SLT  = 3'd5
  } alu_op_t;

  // Equivalente a record en VHDL
  typedef struct packed {
    logic        valid;
    logic [4:0]  rd;
    logic [31:0] data;
  } wb_bus_t;

endpackage


// ----------------------------------------------------------------
// 2) INTERFACE: agrupación limpia de señales entre módulos
// ----------------------------------------------------------------
interface simple_bus_if;
  logic        req;
  logic        we;
  logic [31:0] addr;
  logic [31:0] wdata;
  logic [31:0] rdata;
  logic        ready;

  // Direcciones de uso (modport)
  modport master (
    output req, we, addr, wdata,
    input  rdata, ready
  );

  modport slave (
    input  req, we, addr, wdata,
    output rdata, ready
  );
endinterface


// ----------------------------------------------------------------
// 3) MÓDULO PRINCIPAL DE EJEMPLO
// ----------------------------------------------------------------
module sv_basics_top #(
  parameter int WIDTH = 8,                 // generic en VHDL
  parameter bit USE_PARITY = 1'b1
)(
  input  logic             clk,
  input  logic             rst_n,          // reset activo en 0
  input  logic [WIDTH-1:0] a,
  input  logic [WIDTH-1:0] b,
  input  logic [2:0]       sel,
  output logic [WIDTH-1:0] y,
  output logic             parity
);

  import cpu_types_pkg::*;

  // --------------------------------------------------------------
  // Declaraciones básicas
  // --------------------------------------------------------------
  logic [WIDTH-1:0] sum_c, and_c, or_c, xor_c;
  logic [WIDTH-1:0] reg_q;

  // Vector packed vs arreglo unpacked
  logic [7:0] packed_vec;          // 8 bits juntos
  logic [7:0] mem [0:15];          // memoria: 16 palabras de 8 bits

  // Arreglo multidimensional unpacked
  logic [15:0] lut [0:3][0:1];

  // Typedef para vector reutilizable
  typedef logic [WIDTH-1:0] word_t;
  word_t v1, v2;

  // Struct y enum del package
  wb_bus_t wb;
  alu_op_t alu_op;

  // Constantes locales
  localparam int SHIFT = 2;

  // --------------------------------------------------------------
  // always_comb: lógica combinacional (como process combinacional)
  // --------------------------------------------------------------
  always_comb begin
    sum_c = a + b;
    and_c = a & b;
    or_c  = a | b;
    xor_c = a ^ b;

    // case único (recomendado con default)
    unique case (sel)
      3'd0: y = sum_c;
      3'd1: y = and_c;
      3'd2: y = or_c;
      3'd3: y = xor_c;
      3'd4: y = a << SHIFT;
      3'd5: y = a >> SHIFT;
      default: y = '0;              // '0 = llena con 0 todo el ancho
    endcase

    parity = ^y;                    // reducción XOR
  end

  // --------------------------------------------------------------
  // always_ff: lógica secuencial (flip-flops)
  // --------------------------------------------------------------
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n)
      reg_q <= '0;
    else
      reg_q <= y;
  end

  // --------------------------------------------------------------
  // always_latch: explícito para latch (normalmente evitar en RTL)
  // --------------------------------------------------------------
  logic latch_q, en;
  always_latch begin
    if (en) latch_q <= a[0];
  end

  // --------------------------------------------------------------
  // Assign continuo
  // --------------------------------------------------------------
  assign wb.valid = 1'b1;
  assign wb.rd    = 5'd1;
  assign wb.data  = {{(32-WIDTH){1'b0}}, reg_q};

  // --------------------------------------------------------------
  // for-generate
  // --------------------------------------------------------------
  logic [WIDTH-1:0] inv_bits;
  genvar i;
  generate
    for (i = 0; i < WIDTH; i++) begin : g_inv
      assign inv_bits[i] = ~a[i];
    end
  endgenerate

  // --------------------------------------------------------------
  // if-generate
  // --------------------------------------------------------------
  generate
    if (USE_PARITY) begin : g_with_parity
      // ya calculada arriba, bloque de ejemplo
    end else begin : g_no_parity
      // alternativa sin paridad
    end
  endgenerate

  // --------------------------------------------------------------
  // Conversión / casting
  // --------------------------------------------------------------
  logic signed [WIDTH-1:0] sa, sb;
  logic signed [WIDTH:0]   ssum;

  always_comb begin
    sa   = signed'(a);              // cast
    sb   = signed'(b);
    ssum = sa + sb;
  end

endmodule


// ----------------------------------------------------------------
// 4) SUBMÓDULO con parámetros
// ----------------------------------------------------------------
module adder #(
  parameter int W = 8
)(
  input  logic [W-1:0] a,
  input  logic [W-1:0] b,
  output logic [W:0]   y
);
  assign y = a + b;
endmodule


// ----------------------------------------------------------------
// 5) TESTBENCH mínimo (SystemVerilog)
// ----------------------------------------------------------------
module tb_sv_basics;
  logic clk, rst_n;
  logic [7:0] a, b;
  logic [2:0] sel;
  logic [7:0] y;
  logic parity;

  sv_basics_top #(.WIDTH(8)) dut (
    .clk(clk), .rst_n(rst_n), .a(a), .b(b), .sel(sel), .y(y), .parity(parity)
  );

  // reloj
  initial clk = 0;
  always #5 clk = ~clk;

  // estímulos
  initial begin
    rst_n = 0;
    a = 8'h00; b = 8'h00; sel = 3'd0;
    #20;
    rst_n = 1;

    a = 8'h0A; b = 8'h03; sel = 3'd0; #10; // suma
    sel = 3'd1; #10;                       // and
    sel = 3'd2; #10;                       // or
    sel = 3'd3; #10;                       // xor
    sel = 3'd4; #10;                       // shift left

    $display("y=%0h parity=%0b", y, parity);
    $finish;
  end
endmodule
