module ALU (
    input  wire [31:0] a,
    input  wire [31:0] b,
    input  wire [3:0]  instruccion,
    output reg  [31:0] salida,
    output wire [31:0] multiplicacion_high_part
);
        wire [63:0] mul_u;
        wire signed [31:0] a_s;
        wire signed [31:0] b_s;
        wire signed [63:0] mul_ss;

        assign mul_u = a * b;
        assign a_s = a;
        assign b_s = b;
        assign mul_ss = a_s * b_s;

        // Parte alta de multiplicación con signo (estilo MULH)
        assign multiplicacion_high_part = mul_ss[63:32];

        always @(*) begin
            case (instruccion)
                4'h0: salida = a + b;                    // ADD
                4'h1: salida = a - b;                    // SUB
                4'h2: salida = mul_u[31:0];              // MUL (parte baja)
                4'h3: salida = (b != 0) ? (a / b) : 0;   // DIV
                4'h4: salida = a & b;                    // AND
                4'h5: salida = a | b;                    // OR
                4'h6: salida = a ^ b;                    // XOR
                4'h7: salida = ~a;                       // NOT
                4'h8: salida = a << b[4:0];              // SHL
                4'h9: salida = a >> b[4:0];              // SHR
                4'hA: salida = mul_ss[63:32];            // MULH (parte alta signed*signed)
                4'hB: salida = mul_u[63:32];             // MULHU (parte alta unsigned*unsigned)
                default: salida = 32'b0;                 // NOP
            endcase
        end
endmodule
