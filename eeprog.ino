// Arduino NANO EEPROM programmer.
// (C) 2018 Nandor Licker. All rights reserved.

#define OE    2
#define IO0   3
#define IO7  10
#define WE   11
#define CLK  12
#define DATA 13

#define VERSION     1
#define BUFFER_SIZE 1024

uint8_t data[BUFFER_SIZE];
uint16_t len;



void shift(uint16_t addr)
{
  for (int i = 15; i >= 0; i -= 1) {
    digitalWrite(CLK, LOW);
    digitalWrite(DATA, addr & (1 << i) ? HIGH : LOW);
    digitalWrite(CLK, HIGH);
  }
}

uint8_t read_bus()
{
  uint8_t data = 0;
  for (int i = 0; i < 8; i += 1) {
    pinMode(IO0 + i, INPUT);
    data |= digitalRead(IO0 + i) ? (1 << i) : 0;
  }
  return data;
}

void write(uint16_t addr, uint8_t data)
{
  // Set the address.
  digitalWrite(OE, HIGH);
  shift(addr);
  
  // Write the input.
  for (int i = 0; i < 8; i += 1) {
    pinMode(IO0 + i, OUTPUT);
    digitalWrite(IO0 + i, data & (1 << i) ? HIGH : LOW);
  }

  // Write.
  digitalWrite(WE, LOW);
  delayMicroseconds(1);
  digitalWrite(WE, HIGH);
  delay(10);
}

uint8_t read(uint16_t addr)
{
  digitalWrite(OE, LOW);
  shift(addr);
  uint8_t data = read_bus(); 
  digitalWrite(OE, HIGH);
  return data;
}

bool upload(uint16_t offset)
{
  // Write data.
  for (uint16_t i = 0; i < sizeof(data); i += 64) {
    for (uint8_t j = 0; j < 64; ++j) {
      write(offset + i + j, data[i + j]);
    }
    
    Serial.print('.');
  }

  // Read to verify.
  for (uint16_t i = 0; i < sizeof(data); ++i) {
    if (read(offset + i) != data[i]) {
      return false;
    }
  }
  
  return true;
}

uint16_t serial16()
{
  while (!Serial.available());
  uint8_t lo = Serial.read();
  while (!Serial.available());
  uint8_t hi = Serial.read();
  
  return ((uint16_t)hi << 8) | lo;
}

void setup() 
{
  pinMode(OE,   OUTPUT);
  pinMode(WE,   OUTPUT);
  pinMode(CLK,  OUTPUT);
  pinMode(DATA, OUTPUT);
  
  digitalWrite(WE,  HIGH);
  digitalWrite(CLK, HIGH);

  Serial.setTimeout(10000);
  Serial.begin(115200); 
  while (!Serial); 
}

void loop() {
  switch (Serial.read()) {
    case -1: {
      return;
    }
    // Read version.
    case 'v': {
      Serial.println(VERSION, DEC);
      return;
    }
    // Read buffer size.
    case 'b': {
      Serial.println(BUFFER_SIZE, DEC);
      return;
    }
    // Upload EEPROM.
    case 'u': {
      uint16_t count = serial16();
      if (count % BUFFER_SIZE != 0) {
        Serial.print('n');
        break;
      }
      
      for (uint16_t i = 0; i < count; ++i) {
        if (Serial.readBytes(data, BUFFER_SIZE) != BUFFER_SIZE) {
          Serial.print('n');
          break;
        }
        
        if (upload(i * BUFFER_SIZE)) {
          Serial.print('y');
        } else {
          Serial.print('n');
          break;
        }
      }
      return;
    }
    // Download EEPROM.
    case 'd': {
      uint16_t chunk = serial16();
      uint16_t off = chunk * BUFFER_SIZE;
      
      for (uint16_t i = 0; i < BUFFER_SIZE; ++i) {
        data[i] = read(off + i);
      }
      Serial.write(data, BUFFER_SIZE);
      
      return;
    }
    default: {
      Serial.println("Unknown command");
      return;
    }
  }
}
