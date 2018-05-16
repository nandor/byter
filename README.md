Byter
=====


Byter is an 8-bit computer built mostly out of 7400 series HC and HCT integrated circuits.
It features a 16-bit address bus, 64Kb RAM, up to 32Kb ROM, 8 input ports, and 8 output ports.
The custom architecture includes a hardware stack pointer, program counter, accumulator,
index register (page + offset). CPU clock rates of up to 1Mhz are supported, however by
default the clock is scaled down to 2KHz.  The instruction set is stack-based. Available
peripherals include an 16x2 LCD display, a 4x4 hex keypad, a timer and 8 debug LEDs.

The current implementation includes 77 ICs and ~70m of wiring.

Peripherals are mapped to the following ports:


* **I0**: 8-bit timer
* **I1**: Keypad scan
* **O0**: LCD data
* **O1**: LCD control
* **O2**: Keypad mask


This repository contains a rudimentary assembler, an eeprom uploader and a microcode generator.

![CPU](https://raw.githubusercontent.com/nandor/byter/master/docs/byter.JPG)

![PRG](https://raw.githubusercontent.com/nandor/byter/master/docs/prog.JPG)
