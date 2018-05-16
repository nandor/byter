


def expand(c):
  if not c:
    return ['']

  if c[0] == 'x':
    return ['0' + x for x in expand(c[1:])] + ['1' + x for x in expand(c[1:])]
  else:
    return [c[0] + x for x in expand(c[1:])]


def bin(num, n):
  code = ''
  for i in range(0, n):
    code = ('1' if num & (1 << i) else '0') + code
  return(code)

def hex(str):
  num = 0
  for i in range(0, 8):
    if str[i] == '1':
      num = num | (1 << (8 - i - 1))
  return num
