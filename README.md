**Task Description**
Debug and complete the RTL implementation of a simple AMBA APB-based system.
The agent should modify the RTL files in rtl/ so that the APB system works correctly and passes the provided testbench.
The design contains three modules:
  •	`apb_master`
  •	`apb_slave`
  •	`apb_top`
The `apb_top` module connects the master and slave and forms the top-level design.

The agent must:
  •	Complete the `apb_top` module by instantiating and connecting `apb_master` and `apb_slave`
  •	Fix the APB master FSM so it follows the IDLE → SETUP → ACCESS protocol
  •	Ensure correct read and write transactions
  •	Maintain correct reset behavior
  •	Ensure the RTL compiles and passes all testcases in the testbench
  
**Directory Structure**
sources/    - RTL design files(golden Implementation)
tests/      - Hidden grading scripts
docs/       - APB specification and protocol description

The simulation should complete successfully and all testcases must pass.
