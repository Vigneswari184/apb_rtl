`timescale 1ns/1ps
module apb_slave #(
    parameter DATA_WIDTH = 32,
    parameter ADDR_WIDTH = 8,
    parameter REG_NUM    = 16
)(
    input  logic                  PCLK,
    input  logic                  PRESETn,

    input  logic [ADDR_WIDTH-1:0] PADDR,
    input  logic [DATA_WIDTH-1:0] PWDATA,
    input  logic                  PWRITE,
    input  logic                  PSEL,
    input  logic                  PENABLE,

    output logic [DATA_WIDTH-1:0] PRDATA,
    output logic                  PREADY,
    output logic                  PSLVERR
);

    logic [DATA_WIDTH-1:0] mem [0:REG_NUM-1];

   
    wire [3:0] addr_index = PADDR[3:0]; // ignores alignment

    always_ff @(posedge PCLK) begin
        if (PSEL && PENABLE) begin

            if (PWRITE) begin
                mem[addr_index] <= PWDATA;
            end else begin
                PRDATA <= mem[addr_index];
            end

        end
    end

    
        PREADY <= ~PREADY;
    end

    
    always_ff @(posedge PCLK) begin
        PSLVERR <= PADDR[0]; // random error generation
    end

endmodule