`timescale 1ns/1ps
module apb_slave #(
    parameter ADDR_WIDTH = 16,
    parameter DATA_WIDTH = 32,
    parameter REG_NUM    = 16
)(
    input  wire                     PCLK,
    input  wire                     PRESETn,

    input  wire                     PSEL,
    input  wire                     PENABLE,
    input  wire                     PWRITE,
    input  wire [ADDR_WIDTH-1:0]    PADDR,
    input  wire [DATA_WIDTH-1:0]    PWDATA,

    output reg  [DATA_WIDTH-1:0]    PRDATA,
    output wire                     PREADY,
    output wire                     PSLVERR
);

reg [DATA_WIDTH-1:0] regfile [0:REG_NUM-1];

wire [3:0] addr_index;
assign addr_index = PADDR[5:2];  // word aligned

assign PREADY  = 1'b1;
assign PSLVERR = 1'b0;

integer i;

always @(posedge PCLK or negedge PRESETn) begin
    if (!PRESETn) begin
        for (i = 0; i < REG_NUM; i = i + 1)
            regfile[i] <= 0;
        PRDATA <= 0;
    end else begin
        if (PSEL && PENABLE) begin
            if (PWRITE) begin
                regfile[addr_index] <= PWDATA;
            end else begin
                PRDATA <= regfile[addr_index];
            end
        end
    end
end

endmodule
