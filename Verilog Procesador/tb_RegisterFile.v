`timescale 1ns/1ps

module tb_RegisterFile;
    reg         clk;
    reg         rst;

    reg  [4:0]  rs1_addr;
    reg  [4:0]  rs2_addr;
    wire [31:0] rs1_data;
    wire [31:0] rs2_data;

    reg         rd_we;
    reg  [4:0]  rd_addr;
    reg  [31:0] rd_data;

    RegisterFile dut (
        .clk(clk),
        .rst(rst),
        .rs1_addr(rs1_addr),
        .rs2_addr(rs2_addr),
        .rs1_data(rs1_data),
        .rs2_data(rs2_data),
        .rd_we(rd_we),
        .rd_addr(rd_addr),
        .rd_data(rd_data)
    );

    // Clock
    initial clk = 1'b0;
    always #5 clk = ~clk;

    initial begin
        $dumpfile("RegisterFile_test.vcd");
        $dumpvars(0, tb_RegisterFile);

        // Init
        rst = 1'b1;
        rd_we = 1'b0;
        rd_addr = 5'd0;
        rd_data = 32'd0;
        rs1_addr = 5'd0;
        rs2_addr = 5'd0;

        #12;
        rst = 1'b0;

        // ========================================================
        // TODO A) Escribe x1 = 0x12345678 y luego léelo por rs1
        // ========================================================


        // ========================================================
        // TODO B) Intenta escribir x0 y verifica que siga en 0
        // ========================================================


        // ========================================================
        // TODO C) Escribe y lee x31
        // ========================================================


        // ========================================================
        // TODO D) Prueba que con rd_we=0 no cambie un registro
        // ========================================================


        #20;
        $finish;
    end
endmodule
