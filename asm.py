#!/usr/bin/env python

import sys
from insts import INSTS

targets = {}
by_name = {}
for inst in INSTS:
  by_name[inst.name] = inst

def embed(pattern, bits):
  if not pattern:
    return ''
  if pattern[0] != 'x':
    return pattern[0] + embed(pattern[1:], bits)
  else:
    return str(bits[0]) + embed(pattern[1:], bits[1:])

class Inst(object):
  def __init__(self, op, args):
    self.op = op
    self.args = args

  def get_size(self):
    if len(self.args) == 0:
      return 1
    elif self.op in ['call']:
      return 3
    elif 'x' in by_name[self.op].encoding:
      return len(self.args)
    else:
      return len(self.args) + 1

  def assemble(self, addr):
    encoding = by_name[self.op].encoding
    if 'x' in encoding:
      arg = self.args[0]
      args = self.args[1:]
      num = list(reversed([(arg >> i) & 1 for i in range(encoding.count('x'))]))
      opcode = int(embed(encoding, num), 2)
    else:
      args = self.args
      opcode = int(encoding, 2)
    code = [opcode]
    for idx, arg in zip(range(len(args)), args):
      if isinstance(arg, str):
        if arg.startswith('\''):
          code.append(ord(arg[1]))
        elif self.op in ['jmp', 'jcc']:
          diff = targets[arg].addr - (addr + idx + 2)
          if diff < -128 or diff > 127:
            raise Exception('Invalid target')
          code.append(diff & 0xFF)
        else:
          code.append((targets[arg].addr >> 8) & 0xFF)
          code.append((targets[arg].addr >> 0) & 0xFF)
      else:
        code.append(arg)
    return code

class Block(object):
  def __init__(self):
    self.addr = 0
    self.insts = []

  def get_size(self):
    size = 0
    for inst in self.insts:
      size += inst.get_size()
    return size

block = Block()
blocks = [block]

with open(sys.argv[1], 'r') as f:
  for line in f.readlines():
    tokens = line.strip().split(':')
    labels = [lb.strip() for lb in tokens[:-1] if lb]
    if labels:
      block = Block()
      blocks.append(block)
      for label in labels:
        if label in targets:
          raise Exception("Duplicate label: %s" % label)
        targets[label] = block
    insts = [tk.strip() for tk in tokens[-1].split(';') if tk]
    for inst in insts:
      op, *args = [i for i in inst.split(' ') if i]
      iargs = []
      for arg in args:
        iarg = None
        try:
          iarg = int(arg, 16)
        except:
          try:
            iarg = int(arg, 10)
          except:
            iarg = arg
        iargs.append(iarg)
      if op not in by_name or not by_name[op].cycles:
        raise Exception("Unknown opcode: %s" % op)
      block.insts.append(Inst(op, iargs))

addr = 0
for block in blocks:
  block.addr = addr
  addr += block.get_size()

code = []
addr = 0
for block in blocks:
  for inst in block.insts:
    for byte in inst.assemble(addr):
      code.append(byte)
    addr += inst.get_size()

with open('prog.rom', 'wb') as f:
  f.write(bytearray(code + (1024 - len(code)) * [0]))
