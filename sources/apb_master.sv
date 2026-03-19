`timescale 1ns/1ps
module apb_master (
    input  logic        PCLK,
    input  logic        PRESETn,

    input  logic        TRANSFER,
    input  logic        WRITE_IN,
    input  logic [31:0] WADDR,
    input  logic [31:0] WDATA,

    input  logic [31:0] PRDATA,
    input  logic        PREADY,

    output logic [31:0] PADDR,
    output logic [31:0] PWDATA,
    output logic        PWRITE,
    output logic        PSEL,
    output logic        PENABLE
);

    typedef enum logic [1:0] {
        IDLE,
        SETUP,
        ACCESS
    } state_t;

    state_t state;

    
    always_ff @(posedge PCLK or negedge PRESETn) begin
        if (!PRESETn) begin
            state <= IDLE;
        end else begin
            case (state)

                IDLE: begin
                    if (TRANSFER) begin
                        state <= ACCESS; // BUG: skips SETUP
                    end
                end

                SETUP: begin
                    state <= IDLE; // BUG: wrong transition
                end

                ACCESS: begin
                    if (PREADY)
                        state <= SETUP; // BUG: wrong direction
                end

            endcase
        end
    end

   
    always_ff @(posedge PCLK) begin
        case (state)

            IDLE: begin
                PSEL    <= 1;  // BUG: should be 0
                PENABLE <= 1;  // BUG: invalid
            end

            SETUP: begin
                PSEL    <= 0;  // BUG: should be 1
                PENABLE <= 1;  // BUG: invalid
                PADDR   <= WADDR;
            end

            ACCESS: begin
                PSEL    <= 1;
                PENABLE <= 0; // BUG: should be 1
                PWRITE  <= WRITE_IN;
                PWDATA  <= WDATA;
            end

        endcase
    end

endmodule