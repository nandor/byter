#!/usr/bin/env python

import serial
import sys
import time

cmd = sys.argv[1]
port = sys.argv[2]
file = sys.argv[3]

# Open a new connection. This will reset the arduino.
with serial.Serial(port, 115200, timeout=1) as ser:
  time.sleep(5)
  ser.flush()

  # Check th version number.
  ser.write(b'v')
  version = int(ser.readline())
  if version != 1:
    print('Invalid version.')
    sys.exit(1)

  # Read the block size.
  ser.write(b'b')
  bs = int(ser.readline())

  if cmd == 'u':
    with open(file, 'rb') as inf:
      data = inf.read()
      length = len(data)

      if length > 0xFFFF:
        print('File too large.')
        sys.exit(1)

    length = len(data)
    if length % bs != 0:
      print('Invalid file size')
      sys.exit(1)

    # Upload chunks.
    print("Uploading {} bytes from {}".format(length, file))

    ser.write(b'u')
    ser.write(bytearray([length & 0xFF, length >> 8]))

    chunks = int(length / bs) + (1 if length % bs != 0 else 0)
    for i in range(0, chunks):
      chunk = data[i * bs : (i + 1) * bs]
      ser.write(chunk)

      while True:
        ch = ser.read(1)
        if len(ch) == 0:
          continue

        if ch == b'.':
          sys.stdout.write('.')
          sys.stdout.flush()
        elif ch == b'y':
          sys.stdout.write('\n')
          break
        else:
          sys.stdout.write('\nWrite failed: ' + str(ch) + '\n')
          sys.exit(0)

  if cmd == 'd':
    length = 8192
    with open(file, 'wb') as outf:
      for i in range(0, int(length / bs)):
        ser.write(b'd')
        ser.write(bytearray([i & 0xFF, i >> 8]))
        outf.write(ser.read(bs))
