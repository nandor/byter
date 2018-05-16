#!/usr/bin/env python

from insts import INSTS, NOP
from helper import *



encodings = {}
for inst in INSTS:
  for addr, cycle in inst:
    if addr in encodings:
      print('Duplicate encoding!')
      sys.exit(-1)
    encodings[addr] = cycle

rom = [[], [], [], []]
for addr in range(0x2000):
  encoding = bin(addr, 13)
  if encoding not in encodings:
    code = NOP.encode()
  else:
    code = encodings[encoding].encode()

  for i, b in zip(range(4), (hex(x) for x in code)):
    rom[i].append(b)

for i in range(4):
  with open('micro%d.rom' % i, 'wb') as f:
    f.write(bytearray(rom[i]))

