// define data packet transmission start and end bytes
const byte start_byte = 0x7F; //127
const byte end_byte = 0x80; //128

// define piezo sensor analog read pin
const byte piezoPin1 = A0;
const byte piezoPin2 = A1;
const unsigned long sampleInterval = 1000000 / 1200; // 1,000,000 us / 1200 hz
const word piezo_thres1 = 1; // inclusive
const word piezo_thres2 = 1; // inclusive

// Initiate variables
unsigned long lastSampleTime = 0;
byte cycle_20 = 0; 
byte piezo_adder1 = 0;
bool piezo_bool1 = false;
byte piezo_adder2 = 0;
bool piezo_bool2 = false;
//word piezoArray[19] = {0};
volatile int pulse_count = 0;

// Main loop setup
void setup() {
  
  Serial.begin(115200); //reduce this rate later
  //Serial.setTimeout(1);
  while (!Serial) { /* Wait for Serial to initialize */ }
  // Setup ADC for faster conversion
  ADCSRA = (ADCSRA & 0xF8) | 0x04;          // Set prescaler to 16 for faster conversion
  pinMode(piezoPin1, INPUT);                       // Set A0 as input pin
  pinMode(piezoPin2, INPUT);                       // Set A1 as input pin
}

void loop() {
  unsigned long currentTime = micros();
  if (currentTime - lastSampleTime >= sampleInterval){
    lastSampleTime = currentTime; // update last sample time
    if (cycle_20 == 19){ // 60 Hz loop
      cycle_20 = 0;
      
      // Transmit data
      // Transmit redundant start bytes
      Serial.write(start_byte);
     // Serial.write(start_byte);
     // Serial.write(start_byte);
      
      //uint16_t checksum = 0; // Initialize checksum
     // for (int i = 0; i < 19; i++) {
          // Split 16-bit value into two 8-bit parts
       //   uint8_t highByte = (piezoArray[i] >> 8) & 0xFF; // Get the high byte
      //    uint8_t lowByte = piezoArray[i] & 0xFF; // Get the low byte
          // Update checksum
      //    checksum += highByte + lowByte;
          // Send high byte first, then low byte
      //    Serial.write(highByte);
      //    Serial.write(lowByte);
          // Reset piezoArray[i] to 255 (or any desired value)
       //   piezoArray[i] = 255;
      //}
      
      Serial.write(piezo_adder1);
      //checksum += piezo_adder;
      
      piezo_bool1 = (piezo_adder1 > 0) ? 1 : 0;
      Serial.write(piezo_bool1);
      //checksum += piezo_bool;

      Serial.write(piezo_adder2);
      //checksum += piezo_adder;
      
      piezo_bool2 = (piezo_adder2 > 0) ? 1 : 0;
      Serial.write(piezo_bool2);
      //checksum += piezo_bool;
      
      // Transmit the checksum as two bytes
      //Serial.write((checksum >> 8) & 0xFF); // High byte of checksum
      //Serial.write(checksum & 0xFF); // Low byte of checksum
      
      // Transmit redundant End bytes
      Serial.write(end_byte);
      //Serial.write(end_byte);
      //Serial.write(end_byte);

      // Flush the serial
      Serial.flush();
      piezo_adder1 = 0;
      piezo_adder2 = 0;
    }
    else { // 1200 Hz loop
      cycle_20 += 1;
      // Add piezo calculations here
      //piezoArray[cycle_20-1] = piezo_raw; // append value to piezo array
      word piezo_raw1 = analogRead(piezoPin1); //
      if (piezo_raw1 >= piezo_thres1){
        piezo_adder1 += 1;
      }
      word piezo_raw2 = analogRead(piezoPin2); //
      if (piezo_raw2 >= piezo_thres2){
        piezo_adder2 += 1;
      }
    }
  }
}
