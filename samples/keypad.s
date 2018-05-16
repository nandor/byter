  nop
  imma 0x00
  push
  push

  call lcd_clear
  imma 0x80
  call lcd_cmd
  call lcd_greeting

start:
  imma 0xA8
  call lcd_cmd

  imma  0x01; out 2; in 1; imma 0x0F; and
  jcc   0x4 set_1
  out   3
  push
  imma  0x0E; tst; jcc 0x4 key_1
  imma  0x0D; tst; jcc 0xd key_4
  imma  0x0B; tst; jcc 0xd key_7
  imma 'A'; call lcd_val; jmp start
key_1:
  imma '1'; call lcd_val; jmp start
key_4:
  imma '4'; call lcd_val; jmp start
key_7:
  imma '7'; call lcd_val; jmp start

pad_1:
  jmp start

set_1:
  imma  0x02; out 2; in 1; imma 0x0F; and
  jcc   0x4 pad_1
  out   3
  push
  imma  0x0E; tst; jcc 0x4 key_2
  imma  0x0D; tst; jcc 0xd key_5
  imma  0x0B; tst; jcc 0xd key_8
  imma '0'; call lcd_val; jmp pad_1
key_2:
  imma '2'; call lcd_val; jmp pad_1
key_5:
  imma '5'; call lcd_val; jmp pad_1
key_8:
  imma '8'; call lcd_val; jmp pad_1

lcd_greeting:
  push

  imma 'H'
  call lcd_val
  imma 'e'
  call lcd_val
  imma 'l'
  call lcd_val
  imma 'l'
  call lcd_val
  imma 'o'
  call lcd_val
  imma ','
  call lcd_val
  imma 0x20
  call lcd_val
  imma 'w'
  call lcd_val
  imma 'o'
  call lcd_val
  imma 'r'
  call lcd_val
  imma 'l'
  call lcd_val
  imma 'd'
  call lcd_val
  imma '!'
  call lcd_val

  pop
  ret

lcd_clear:
  push

  imma 0x38
  call lcd_cmd
  imma 0x38
  call lcd_cmd
  imma 0x38
  call lcd_cmd
  imma 0x38
  call lcd_cmd

  imma 0x0C
  call lcd_cmd
  imma 0x01
  call lcd_cmd
  imma 0x06
  call lcd_cmd

  pop
  ret

lcd_cmd:
  push
  out 0
  imma 0x0; out 1;
  imma 0x4; out 1;
  imma 0x0; out 1;
  pop
  ret

lcd_val:
  push
  out 0
  imma 0x0; out 1;
  imma 0x5; out 1;
  imma 0x0; out 1;
  pop
  ret
