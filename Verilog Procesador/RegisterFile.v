module RegisterFile (
    input  wire        clk,
    input  wire        rst,

    // Read ports
    input  wire [4:0]  rs1_addr,
    input  wire [4:0]  rs2_addr,
    output wire [31:0] rs1_data,
    output wire [31:0] rs2_data,

    // Write port
    input  wire        rd_we,
    input  wire [4:0]  rd_addr,
    input  wire [31:0] rd_data
);

    // ============================================================
    // TODO 1) Banco de registros: 32 registros de 32 bits
    // Sugerencia: reg [31:0] regs [0:31];
    // ============================================================
    reg [31:0] 
        regs [0:31];

     // Lectura combinacional
    assign rs1_data = (rs1_addr == 5'd0) ? 32'b0 : regs[rs1_addr];
    assign rs2_data = (rs2_addr == 5'd0) ? 32'b0 : regs[rs2_addr];

    // ============================================================
    // TODO 2) Lectura combinacional de rs1 y rs2
    // Requisito: x0 siempre debe leer 0
    // Ejemplo esperado:
    //   rs1_addr == 0 -> rs1_data = 0
    //   rs2_addr == 0 -> rs2_data = 0
    // ============================================================


    // ============================================================
    // TODO 3) Escritura secuencial en flanco positivo
    // if (rd_we && rd_addr != 0) regs[rd_addr] <= rd_data;
    // Requisito: nunca escribir x0
    // ============================================================


    // ============================================================
    // TODO 4) Reset (opcional para síntesis, útil para simulación)
    // Si usas reset, puedes limpiar regs[1..31] a 0.
    // ============================================================
    
endmodule
