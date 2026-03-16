**APB System Specification**
**1. Overview**
This design implements a simple AMBA APB-based system consisting of:
•	apb_master
•	apb_slave
•	apb_top

The APB master initiates read and write transactions to the APB slave.
The slave contains a small register file that can be accessed using the APB protocol.
The apb_top module connects the master and slave through the APB bus.

**2. Module Descriptions**
**2.1 apb_top**
The apb_top module connects the APB master and APB slave and routes the APB bus signals between them.
**Inputs:**
•	`PCLK`– System clock
•	`PRESET_n` – Active-low reset
•	`TRANSFER` – Indicates a transaction request
•	`WADDR` – Address for read/write operation
•	`WDATA` – Data to be written
•	`WRITE_IN` – Transaction type

1 → Write
0 → Read

**Outputs**
•	`PRDATA`– Read data returned from the slave
•	`PSELx` – Slave select signal
•	`PENABLE` – Enable signal for access phase
•	Internal Bus Signals

The following APB signals connect the master and slave:
•	`PADDR`
•	`PWDATA`
•	`PRDATA`
•	`PWRITE`
•	`PSELx`
•	`PENABLE`
•	`PREADY`
•	`PSLVERR`

**The apb_top module must instantiate:**

•	one apb_master
•	one apb_slave

and connect them correctly.

**3. APB Protocol Behavior**
The APB protocol operates in three phases.
**3.1 IDLE Phase**
•	`PSELx` = 0
•	`PENABLE` = 0
Master waits for a transaction request (TRANSFER).

**3.2 SETUP Phase**
•	`PSELx` = 1
•	`PENABLE` = 0
Address (PADDR) and control signals become valid.
Write/read control (PWRITE) is set.

**3.3 ACCESS Phase**
•	`PSELx` = 1
•	`PENABLE` = 1
Transaction completes when PREADY = 1.

**4. APB Master Behavior**
The APB master implements a finite state machine (FSM) with three states:
•	IDLE
•	SETUP
•	ACCESS

**State Transitions**
IDLE → SETUP
•	When TRANSFER = 1.
SETUP → ACCESS
•	After one clock cycle.
ACCESS → IDLE
•	When PREADY = 1.

**Write Transaction**
Conditions:	
•	`WRITE_IN` = 1
Behavior:
•	`PWRITE` = 1
•	`PADDR` is set to WADDR
•	`PWDATA` is set to WDATA
•	Data is written to the slave during the ACCESS phase.

**Read Transaction**
Conditions:
•	`WRITE_IN` = 0
Behavior:
•	`PWRITE` = 0
•	`PADDR` is set to WADDR
•	Data returned from the slave (PRDATA) must be captured in RDATA.

**5. APB Slave Behavior**
The slave contains a register file.

**Register File**
•	Number of registers: `REG_NUM`
Register width:
`DATA_WIDTH`
Registers are word-aligned.

Register index is derived from:
•	PADDR[ADDR_WIDTH-1:2]

**Write Operation**
A write occurs when:
•	`PSELx` = 1
•	`PENABLE` = 1
•	`PWRITE` = 1
Behavior:
•	PWDATA is written into the selected register.

**Read Operation**
A read occurs when:
•	`PSELx` = 1
•	`PENABLE` = 1
•	`PWRITE` = 0

**Behavior:**
•	Data from the selected register is returned on PRDATA.

**6. Response Signals**
For this simplified design:
•	`PREADY` = 1 (slave always ready)
•	`PSLVERR` = 0 (no error response)

**7. Reset Behavior**
When PRESET_n = 0:
•	All registers are cleared to 0
•	`PRDATA` = 0
•	`PSLVERR` = 0
•	`PREADY` = 1

**8. Testbench Requirement**
The corrected RTL implementation must:
•	Compile successfully
•	Pass all provided testcases in the tests directory
•	Produce correct read/write behavior for the APB slave register file.
