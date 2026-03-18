`timescale 1ns/1ps
module apb_top (
    input  wire         PCLK,
    input  wire         PRESETn,

    input  wire         TRANSFER,
    input  wire         WRITE_IN,
    input  wire [15:0]  WADDR,
    input  wire [31:0]  WDATA,

    output wire [31:0]  RDATA,
    output wire         PREADY,
    output wire [31:0]  PRDATA,
    output wire         PENABLE
);

wire        PSEL;
wire        PWRITE;
wire [15:0] PADDR;
wire [31:0] PWDATA;

wire [31:0] PRDATA_s0, PRDATA_s1, PRDATA_s2, PRDATA_s3;
wire        PREADY_s0, PREADY_s1, PREADY_s2, PREADY_s3;

reg  [31:0] PRDATA_mux;
reg         PREADY_mux;

// Instantiate MASTER
apb_master master (
    .PCLK(PCLK),
    .PRESETn(PRESETn),
    .TRANSFER(TRANSFER),
    .WRITE_IN(WRITE_IN),
    .WADDR(WADDR),
    .WDATA(WDATA),
    .PSEL(PSEL),
    .PENABLE(PENABLE),
    .PWRITE(PWRITE),
    .PADDR(PADDR),
    .PWDATA(PWDATA),
    .PREADY(PREADY_mux),
    .PRDATA(PRDATA_mux),
    .RDATA(RDATA)
);

// Address decode: flat 64-register space (addr/4 = 0..63) -> slave = word_index[5:4], reg = word_index[3:0]
wire [1:0] sel;
assign sel = PADDR[7:6];

// Slaves
apb_slave s0 (.PCLK(PCLK), .PRESETn(PRESETn),
    .PSEL(PSEL & (sel==2'b00)), .PENABLE(PENABLE), .PWRITE(PWRITE),
    .PADDR(PADDR), .PWDATA(PWDATA),
    .PRDATA(PRDATA_s0), .PREADY(PREADY_s0), .PSLVERR()
);

apb_slave s1 (.PCLK(PCLK), .PRESETn(PRESETn),
    .PSEL(PSEL & (sel==2'b01)), .PENABLE(PENABLE), .PWRITE(PWRITE),
    .PADDR(PADDR), .PWDATA(PWDATA),
    .PRDATA(PRDATA_s1), .PREADY(PREADY_s1), .PSLVERR()
);

apb_slave s2 (.PCLK(PCLK), .PRESETn(PRESETn),
    .PSEL(PSEL & (sel==2'b10)), .PENABLE(PENABLE), .PWRITE(PWRITE),
    .PADDR(PADDR), .PWDATA(PWDATA),
    .PRDATA(PRDATA_s2), .PREADY(PREADY_s2), .PSLVERR()
);

apb_slave s3 (.PCLK(PCLK), .PRESETn(PRESETn),
    .PSEL(PSEL & (sel==2'b11)), .PENABLE(PENABLE), .PWRITE(PWRITE),
    .PADDR(PADDR), .PWDATA(PWDATA),
    .PRDATA(PRDATA_s3), .PREADY(PREADY_s3), .PSLVERR()
);

assign PREADY  = PREADY_mux;
assign PRDATA  = PRDATA_mux;

// MUX logic
always @(*) begin
    case (sel)
        2'b00: begin PRDATA_mux = PRDATA_s0; PREADY_mux = PREADY_s0; end
        2'b01: begin PRDATA_mux = PRDATA_s1; PREADY_mux = PREADY_s1; end
        2'b10: begin PRDATA_mux = PRDATA_s2; PREADY_mux = PREADY_s2; end
        2'b11: begin PRDATA_mux = PRDATA_s3; PREADY_mux = PREADY_s3; end
    endcase
end

endmodule
