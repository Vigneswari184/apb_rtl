`timescale 1ns/1ps
module apb_master (
    input  wire         PCLK,
    input  wire         PRESETn,

    input  wire         TRANSFER,
    input  wire         WRITE_IN,
    input  wire [15:0]  WADDR,
    input  wire [31:0]  WDATA,

    input  wire [31:0]  PRDATA,
    input  wire         PREADY,

    output reg          PSEL,
    output reg          PENABLE,
    output reg          PWRITE,
    output reg  [15:0]  PADDR,
    output reg  [31:0]  PWDATA,
    output reg  [31:0]  RDATA
);

    localparam [1:0] IDLE   = 2'b00,
                    SETUP  = 2'b01,
                    ACCESS = 2'b10;

    reg [1:0] state;

    always @(posedge PCLK or negedge PRESETn) begin
        if (!PRESETn) begin
            state   <= IDLE;
            PSEL    <= 0;
            PENABLE <= 0;
            PWRITE  <= 0;
            PADDR   <= 0;
            PWDATA  <= 0;
            RDATA   <= 0;
        end else begin
            case (state)
                IDLE: begin
                    PSEL    <= 0;
                    PENABLE <= 0;
                    if (TRANSFER) begin
                        state <= SETUP;
                    end
                end

                SETUP: begin
                    PSEL    <= 1;
                    PENABLE <= 0;
                    PADDR   <= WADDR;
                    PWRITE  <= WRITE_IN;
                    PWDATA  <= WDATA;
                    state   <= ACCESS;
                end

                ACCESS: begin
                    PENABLE <= 1;
                    if (PREADY) begin
                        if (!PWRITE)
                            RDATA <= PRDATA;
                        state <= IDLE;
                    end
                end
            endcase
        end
    end

endmodule
