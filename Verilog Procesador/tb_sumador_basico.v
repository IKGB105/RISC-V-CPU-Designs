`timescale 1ms/1ns

module tb_sumador_basico;
    reg  [7:0] a;
    reg  [7:0] b;
    wire [8:0] suma;
    wire [15:0] multiplicacion;

    sumador_basico dut (
        .a(a),
        .b(b),
        .suma(suma),
        .multiplicacion(multiplicacion)
    );

    initial begin
        $dumpfile("sumador_basico.vcd");
        $dumpvars(0, tb_sumador_basico);

        a = 8'd0;   b = 8'd0;   #10;
        a = 8'd10;  b = 8'd5;   #10;
        a = 8'd255; b = 8'd1;   #10;
        a = 8'd100; b = 8'd50;  #10;

        $finish;
    end
endmodule
