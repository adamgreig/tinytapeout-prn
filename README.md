# Tiny PRN generator for TinyTapeout

See original template repository [here](https://github.com/mattvenn/wokwi-verilog-gds-test/blob/main/README.md).

This project use Amaranth to generate a single verilog file for inclusion.
The module generates the GPS C/A PRN sequences.

* IN0: Clock
* IN1: Reset
* IN2..5: GPS PRN number select (0..31 for PRN1..32)
* OUT0: G1 output
* OUT1: G2 output
* OUT2: Selected PRN output
