`timescale 1ns/1ps

module apb_top #(
    parameter ADDR_WIDTH = 8,
    parameter DATA_WIDTH = 32,
    parameter REG_NUM    = 4
)(
    input  wire                  PCLK,
    input  wire                  PRESET_n,
    input  wire                  TRANSFER,
    input  wire [ADDR_WIDTH-1:0] WADDR,
    input  wire [DATA_WIDTH-1:0] WDATA,
    input  wire                  WRITE_IN,
    output wire [DATA_WIDTH-1:0] PRDATA,
    output wire                  PSELx,
    output wire                  PENABLE
);
    // APB bus between master and slave
    wire [ADDR_WIDTH-1:0] PADDR;
    wire [DATA_WIDTH-1:0] PWDATA;
    wire                  PWRITE;
    wire                  PREADY;
    wire                  PSLVERR;

   //
    
endmodule