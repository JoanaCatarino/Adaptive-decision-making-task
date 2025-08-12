# -*- coding: utf-8 -*-
"""
Created on Tue Aug 12 15:30:54 2025

@author: JoanaCatarino
"""

// ----- Piezo dual-channel sender @ 60 Hz frames (1200 Hz ADC inner loop) -----
// Packet (6 bytes): [0]0x7F, [1]adder1(0..19), [2]first_idx1(0..18 or 255 if none),
//                   [3]adder2(0..19), [4]first_idx2(0..18 or 255), [5]0x80

const byte start_byte = 0x7F;
const byte end_byte   = 0x80;

const byte piezoPin1 = A0;
const byte piezoPin2 = A1;

// 1200 Hz subsampling; 20 subsamples per frame -> 60 Hz frames
const unsigned long sampleInterval = 1000000UL / 1200UL;

// >>> Tune these thresholds (start around 50–150, then adjust) <<<
const word piezo_thres1 = 80;
const word piezo_thres2 = 80;

unsigned long lastSampleTime = 0;
byte   cycle_20    = 0;     // 0..19 within a frame
byte   piezo_adder1 = 0;    // 0..19 hits within current frame
byte   piezo_adder2 = 0;    // 0..19
byte   first_idx1   = 255;  // 0..18 first-hit index; 255 means "no hit"
byte   first_idx2   = 255;

void setup() {
  Serial.begin(115200);
  while (!Serial) {}

  // faster ADC (prescaler /16)
  ADCSRA = (ADCSRA & 0xF8) | 0x04;

  pinMode(piezoPin1, INPUT);
  pinMode(piezoPin2, INPUT);
}

void sendFrame() {
  Serial.write(start_byte);
  Serial.write(piezo_adder1);
  Serial.write(first_idx1);
  Serial.write(piezo_adder2);
  Serial.write(first_idx2);
  Serial.write(end_byte);
  Serial.flush();
}

void resetFrameAccumulators() {
  piezo_adder1 = 0;
  piezo_adder2 = 0;
  first_idx1   = 255;
  first_idx2   = 255;
  cycle_20     = 0;
}

void loop() {
  unsigned long now = micros();
  if (now - lastSampleTime < sampleInterval) return;
  lastSampleTime = now;

  // inner 1200 Hz subsample
  cycle_20++; // goes 1..20
  word v1 = analogRead(piezoPin1);
  if (v1 >= piezo_thres1) {
    if (piezo_adder1 < 255) piezo_adder1++;
    if (first_idx1 == 255) first_idx1 = cycle_20 - 1; // 0-based
  }

  word v2 = analogRead(piezoPin2);
  if (v2 >= piezo_thres2) {
    if (piezo_adder2 < 255) piezo_adder2++;
    if (first_idx2 == 255) first_idx2 = cycle_20 - 1;
  }

  if (cycle_20 >= 20) {     // every 20 subsamples -> 60 Hz frame
    sendFrame();
    resetFrameAccumulators();
  }
}
