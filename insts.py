# This file is part of the byter project.
# Licensing information can be found in the LICENSE file.
# (C) 2018 Nandor Licker. All rights reserved.

from helper import *



DATA_PC_LO = '000'
DATA_PC_HI = '001'
DATA_IO    = '010'
DATA_MDR   = '011'
DATA_ALU   = '100'

ADDR_SP    = '00'
ADDR_SPO   = '01'
ADDR_PO    = '10'
ADDR_PC    = '11'

MEM_ROM    = '00'
MEM_RAM    = '01'
MEM_MSR    = '10'

ALU_C0     = '10'
ALU_C1     = '11'
ALU_CIN    = '00'

ALU_ID     = '00'
ALU_SHR    = '10'
ALU_SHL    = '11'



class Cycle(object):
  def __init__(
      self,
      state,
      cond='x',
      preg='1',
      data='xxx',
      addr='xx',
      pc_ldlo='1',
      pc_ldhi='1',
      pc_mux='0',
      pc_inc='0',
      mem='xx',
      io_wr='0',
      po_ldp='1',
      po_ldo='1',
      sp_dec='1',
      sp_inc='1',
      mem_wr='1',
      alu_c='xx',
      alu_m='1',
      alu_mux='xx',
      alu_flag='1',
      alu_wr='1'):
    self.state    = state
    self.cond     = cond
    self.preg     = preg
    self.data     = data
    self.addr     = addr
    self.pc_ldlo  = pc_ldlo
    self.pc_ldhi  = pc_ldhi
    self.pc_mux   = pc_mux
    self.pc_inc   = pc_inc
    self.mem      = mem
    self.io_wr    = io_wr
    self.po_ldp   = po_ldp
    self.po_ldo   = po_ldo
    self.sp_dec  = sp_dec
    self.sp_inc  = sp_inc
    self.mem_wr   = mem_wr
    self.alu_c    = alu_c
    self.alu_m    = alu_m
    self.alu_mux  = alu_mux
    self.alu_flag = alu_flag
    self.alu_wr   = alu_wr

  def encode(self):
    e0 = self.data + self.preg + bin(self.state, 4)
    e1 = self.mem + self.pc_inc + self.pc_mux + self.pc_ldhi + self.pc_ldlo + self.addr
    e2 = '00' + self.mem_wr + self.sp_inc + self.sp_dec + self.po_ldp + self.po_ldo + self.io_wr
    e3 = self.alu_wr + self.alu_flag + self.alu_mux + '0' + self.alu_m + self.alu_c
    return [x.replace('x', '0') for x in (e0, e1, e2, e3)]


class Inst(object):

  def __init__(self, name, encoding, cycles=None):
    self.name = name
    self.encoding = encoding
    self.cycles = cycles

  def __iter__(self):
    for idx, cycle in zip(range(len(self.cycles)), self.cycles):
      for code in expand(self.encoding):
        for addrs in expand(cycle.cond + bin(idx, 4) + code):
          yield(addrs, cycle)

NOP = Cycle(0x1, addr=ADDR_PC, mem=MEM_ROM, preg='0', pc_inc='1')

INSTS = [
  Inst('nop',   '00000000', cycles=[ NOP ]),
  Inst('push',  '00000001', cycles=[
    Cycle(0x1, addr=ADDR_PC, mem=MEM_ROM, preg='0', pc_inc='1'),
    Cycle(0x2, data=DATA_ALU, sp_dec='0'),
    Cycle(0x3, data=DATA_ALU, addr=ADDR_SP, mem=MEM_MSR, mem_wr='0'),
    Cycle(0x0, data=DATA_ALU, addr=ADDR_SP, mem=MEM_MSR, mem_wr='1')
  ]),
  Inst('stkw',  '00000010', cycles=[]),
  Inst('memw',  '00000011', cycles=[]),
  Inst('call',  '00000100', cycles=[
    Cycle(0x1, addr=ADDR_PC, mem=MEM_ROM, preg='0', pc_inc='1'),
    Cycle(0x2, data=DATA_PC_LO, sp_dec='0', po_ldo='0'),
    Cycle(0x3, data=DATA_PC_LO, addr=ADDR_SP, mem=MEM_MSR, mem_wr='0'),
    Cycle(0x4, data=DATA_PC_HI, addr=ADDR_SP, mem=MEM_MSR, mem_wr='1', sp_dec='0'),
    Cycle(0x5, data=DATA_PC_HI, addr=ADDR_SP, mem=MEM_MSR, mem_wr='0', po_ldp='0'),
    Cycle(0x6, addr=ADDR_SP, mem=MEM_MSR, mem_wr='1', pc_inc='1'),
    Cycle(0x7, addr=ADDR_PC, mem=MEM_ROM),
    Cycle(0x8, addr=ADDR_PO, mem=MEM_ROM, data=DATA_MDR, pc_ldlo='0'),
    Cycle(0x0, data=DATA_MDR, pc_ldhi='0')
  ]),
  Inst('ret',   '00000101', cycles=[
    Cycle(0x1, addr=ADDR_PC, mem=MEM_ROM, preg='0', pc_inc='1'),
    Cycle(0x2, addr=ADDR_SP, mem=MEM_RAM, sp_inc='0'),
    Cycle(0x3, addr=ADDR_SP, mem=MEM_RAM, data=DATA_MDR, pc_ldhi='0'),
    Cycle(0x4, data=DATA_MDR, pc_ldlo='0', sp_inc='0'),
    Cycle(0x5, addr=ADDR_PC, pc_inc='1'),
    Cycle(0x0, addr=ADDR_PC, pc_inc='1')
  ]),
  Inst('jmp',   '00000110', cycles=[
    Cycle(0x1, addr=ADDR_PC, mem=MEM_ROM, preg='0', pc_inc='1'),
    Cycle(0x2, addr=ADDR_PC, mem=MEM_ROM),
    Cycle(0x0, data=DATA_MDR, pc_ldlo='0', pc_ldhi='0', pc_mux='1'),
  ]),
  Inst('immp',  '00000111', cycles=[]),
  Inst('in',    '00001xxx', cycles=[
    Cycle(0x1, addr=ADDR_PC, mem=MEM_ROM, preg='0', pc_inc='1'),
    Cycle(0x2, data=DATA_IO, sp_dec='0'),
    Cycle(0x3, data=DATA_IO, addr=ADDR_SP, mem=MEM_MSR, mem_wr='0'),
    Cycle(0x0, data=DATA_IO, addr=ADDR_SP, mem=MEM_MSR, mem_wr='1')
  ]),
  Inst('out',   '00010xxx', cycles=[
    Cycle(0x1, addr=ADDR_PC, mem=MEM_ROM, preg='0', pc_inc='1'),
    Cycle(0x0, data=DATA_ALU, io_wr='1'),
  ]),
  Inst('immo',  '00011000', cycles=[]),
  Inst('immpo', '00011001', cycles=[]),
  Inst('dsc',   '00011010', cycles=[
    Cycle(0x1, addr=ADDR_PC, mem=MEM_ROM, preg='0', pc_inc='1'),
    Cycle(0x0, sp_inc='0')
  ]),
  Inst('jcc',   '0010xxxx', cycles=[
    Cycle(0x1, addr=ADDR_PC, mem=MEM_ROM, preg='0', pc_inc='1'),
    Cycle(0x2, addr=ADDR_PC, mem=MEM_ROM, pc_inc='1'),
    Cycle(0x0, cond='1', data=DATA_MDR, pc_ldlo='0', pc_ldhi='0', pc_mux='1'),
  ]),
  Inst('not',   '01000000', cycles=[]),
  Inst('nor',   '01000001', cycles=[
    Cycle(0x1, addr=ADDR_PC, mem=MEM_ROM, preg='0', pc_inc='1'),
    Cycle(0x2, addr=ADDR_SP, mem=MEM_RAM, sp_inc='1'),
    Cycle(0x0, data=DATA_MDR, alu_wr='0', alu_flag='0', alu_m='1', alu_mux='00')
  ]),
  Inst('nand',  '01000010', cycles=[
    Cycle(0x1, addr=ADDR_PC, mem=MEM_ROM, preg='0', pc_inc='1'),
    Cycle(0x2, addr=ADDR_SP, mem=MEM_RAM, sp_inc='1'),
    Cycle(0x0, data=DATA_MDR, alu_wr='0', alu_flag='0', alu_m='1', alu_mux='00')
  ]),
  Inst('xor',   '01000110', cycles=[
    Cycle(0x1, addr=ADDR_PC, mem=MEM_ROM, preg='0', pc_inc='1'),
    Cycle(0x2, addr=ADDR_SP, mem=MEM_RAM, sp_inc='1'),
    Cycle(0x0, data=DATA_MDR, alu_wr='0', alu_flag='0', alu_m='1', alu_mux='00')
  ]),
  Inst('sub',   '01010110', cycles=[]),
  Inst('sbc',   '01100110', cycles=[]),
  Inst('cmp',   '01110110', cycles=[
    Cycle(0x1, addr=ADDR_PC, mem=MEM_ROM, preg='0', pc_inc='1'),
    Cycle(0x2, addr=ADDR_SP, mem=MEM_RAM),
    Cycle(0x0, data=DATA_MDR, alu_flag='0', alu_m='0', alu_mux='00', alu_c='11')
  ]),
  Inst('add',   '01001001', cycles=[]),
  Inst('adc',   '01011001', cycles=[]),
  Inst('nxor',  '01101001', cycles=[
    Cycle(0x1, addr=ADDR_PC, mem=MEM_ROM, preg='0', pc_inc='1'),
    Cycle(0x2, addr=ADDR_SP, mem=MEM_RAM, sp_inc='1'),
    Cycle(0x0, data=DATA_MDR, alu_wr='0', alu_flag='0', alu_m='1', alu_mux='00')
  ]),
  Inst('imma',  '01001010', cycles=[
    Cycle(0x1, addr=ADDR_PC, mem=MEM_ROM, preg='0', pc_inc='1'),
    Cycle(0x2, addr=ADDR_PC, mem=MEM_ROM, pc_inc='1'),
    Cycle(0x0, data=DATA_MDR, alu_wr='0', alu_flag='0', alu_m='1', alu_mux='00'),
  ]),
  Inst('and',   '01001011', cycles=[
    Cycle(0x1, addr=ADDR_PC, mem=MEM_ROM, preg='0', pc_inc='1'),
    Cycle(0x2, addr=ADDR_SP, mem=MEM_RAM, sp_inc='1'),
    Cycle(0x0, data=DATA_MDR, alu_wr='0', alu_flag='0', alu_m='1', alu_mux='00')
  ]),
  Inst('tst',   '01011011', cycles=[
    Cycle(0x1, addr=ADDR_PC, mem=MEM_ROM, preg='0', pc_inc='1'),
    Cycle(0x2, addr=ADDR_SP, mem=MEM_RAM),
    Cycle(0x0, data=DATA_MDR, alu_flag='0', alu_m='1', alu_mux='00')
  ]),
  Inst('or',    '01001110', cycles=[
    Cycle(0x1, addr=ADDR_PC, mem=MEM_ROM, preg='0', pc_inc='1'),
    Cycle(0x2, addr=ADDR_SP, mem=MEM_RAM, sp_inc='1'),
    Cycle(0x0, data=DATA_MDR, alu_wr='0', alu_flag='0', alu_m='1', alu_mux='00')
  ]),
  Inst('pop',   '10001010', cycles=[
    Cycle(0x1, addr=ADDR_PC, mem=MEM_ROM, preg='0', pc_inc='1'),
    Cycle(0x2, addr=ADDR_SP, mem=MEM_RAM, sp_inc='0'),
    Cycle(0x0, data=DATA_MDR, alu_wr='0', alu_flag='1', alu_m='1', alu_mux='00')
  ]),
  Inst('stkr',  '10011010', cycles=[]),
  Inst('memr',  '10101010', cycles=[]),
  Inst('romr',  '10111010', cycles=[]),
  Inst('shl',   '11001010', cycles=[]),
  Inst('shr',   '11011010', cycles=[]),
  Inst('sal',   '11101010', cycles=[]),
  Inst('sar',   '11111010', cycles=[]),
]
