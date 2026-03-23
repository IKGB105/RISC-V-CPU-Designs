`timescale 1ns/1ps

module tb_ALU;
    reg  [31:0] a;
    reg  [31:0] b;
    reg  [3:0]  instruccion;
    wire [31:0] salida;
    wire [31:0] multiplicacion_high_part;

    ALU dut (
        .a(a),
        .b(b),
        .instruccion(instruccion),
        .salida(salida),
        .multiplicacion_high_part(multiplicacion_high_part)
    );

    initial begin
        $dumpfile("ALU_test.vcd");
        $dumpvars(0, tb_ALU);

        // ADD
        a = 32'd10; b = 32'd5; instruccion = 4'h0; #10;
        // SUB
        a = 32'd10; b = 32'd7; instruccion = 4'h1; #10;
        // MUL (low 32)
        a = 32'h0001_0002; b = 32'h0000_0003; instruccion = 4'h2; #10;
        // MULH signed*signed (high 32)
        a = 32'hFFFF_FFFE; b = 32'h0000_0004; instruccion = 4'hA; #10;
        // MULHU unsigned*unsigned (high 32)
        a = 32'hFFFF_FFFE; b = 32'h0000_0004; instruccion = 4'hB; #10;
        // DIV
        a = 32'd100; b = 32'd10; instruccion = 4'h3; #10;
        // AND
        a = 32'hF0F0_F0F0; b = 32'h0FF0_0FF0; instruccion = 4'h4; #10;
        // OR
        a = 32'hF0F0_0000; b = 32'h0FF0_000F; instruccion = 4'h5; #10;
        // XOR
        a = 32'hAAAA_AAAA; b = 32'h5555_5555; instruccion = 4'h6; #10;
        // SHL
        a = 32'h0000_0001; b = 32'd4; instruccion = 4'h8; #10;
        // SHR
        a = 32'h8000_0000; b = 32'd4; instruccion = 4'h9; #10;

        $finish;
    end
endmodule
