# -*- coding: utf-8 -*-
"""
Created on Fri Aug  8 16:00:53 2025

@author: JoanaCatarino
"""

// --- Piezo → Raspberry Pi streaming (sensitive + stable) ---
// Format unchanged: [start_byte][adder1][bool1][adder2][bool2][end_byte] @ 60 Hz
// Internal sampling: 1200 Hz, accumulate hits into adder per 20-sample block

#include <math.h>  // for fabsf

// define data packet transmission start and end bytes
const byte start_byte = 0x7F; //127
const byte end_byte   = 0x80; //128

// define piezo sensor analog read pin
const byte piezoPin1 = A0;
const byte piezoPin2 = A1;

// 1200 Hz inner loop -> 833 us period
const unsigned long sampleInterval = 1000000UL / 1200; // microseconds

// Kept for compatibility (not used for the adaptive threshold path)
const word piezo_thres1 = 1; // inclusive
const word piezo_thres2 = 1; // inclusive

// Initiate variables
unsigned long lastSampleTime = 0;
byte cycle_20 = 0; 

byte piezo_adder1 = 0;
bool piezo_bool1  = false;

byte piezo_adder2 = 0;
bool piezo_bool2  = false;

// volatile int pulse_count = 0; // (unused but kept if you rely on it elsewhere)

// ---------- Sensitivity controls ----------
// Exponential moving averages for baseline & noise
// Smaller alpha/beta -> slower tracking (more stable); larger -> faster
const float alpha = 0.01f;  // baseline EMA speed
const float beta  = 0.01f;  // deviation EMA speed
float base1 = 0.0f, base2 = 0.0f;
float noise1 = 1.0f, noise2 = 1.0f;

// Sensitivity factor (threshold = baseline + k*noise)
// Lower k = more sensitive; higher k = stricter
float k = 3.0f;

// Minimum noise floor to avoid "stuck" thresholds if very quiet
const float noise_floor = 1.0f;

// --------- Helpers ---------
inline word readPiezoAverage2(byte pin) {
  // Simple 2-sample average to reduce noise without adding noticeable latency
  word a = analogRead(pin);
  word b = analogRead(pin);
  return (word)((a + b) >> 1);
}

void setup() {
  Serial.begin(115200);
  while (!Serial) { /* Wait for Serial to initialize (for Leonardo/Micro), harmless elsewhere */ }

  // Optional: if your signal is well below 1.1V and properly clamped/divided, you can increase resolution:
  // analogReference(INTERNAL); // ⚠️ Only if input < 1.1V with proper clamping/divider

  // ADC prescaler: use 64 (≈ 250 kHz ADC clock on 16 MHz AVR). Cleaner than 16, fast enough for 1200 Hz.
  ADCSRA = (ADCSRA & 0xF8) | 0x06;  // 0x06 = prescaler 64

  pinMode(piezoPin1, INPUT);
  pinMode(piezoPin2, INPUT);

  // Initialize baselines with first reads to avoid large start-up transients
  word init1 = analogRead(piezoPin1);
  word init2 = analogRead(piezoPin2);
  base1 = (float)init1;
  base2 = (float)init2;
  noise1 = 2.0f; // small initial noise guess
  noise2 = 2.0f;
}

void loop() {
  unsigned long currentTime = micros();
  if (currentTime - lastSampleTime >= sampleInterval) {
    lastSampleTime = currentTime; // update last sample time

    if (cycle_20 == 19) { // 60 Hz packet (after 20 * 1200Hz samples)
      cycle_20 = 0;

      // --- Transmit data (format unchanged) ---
      Serial.write(start_byte);

      Serial.write(piezo_adder1);
      piezo_bool1 = (piezo_adder1 > 0) ? 1 : 0;
      Serial.write(piezo_bool1);

      Serial.write(piezo_adder2);
      piezo_bool2 = (piezo_adder2 > 0) ? 1 : 0;
      Serial.write(piezo_bool2);

      Serial.write(end_byte);

      Serial.flush();

      // reset adders for next 60 Hz window
      piezo_adder1 = 0;
      piezo_adder2 = 0;

    } else { // 1200 Hz loop body
      cycle_20 += 1;

      // ---- Read sensors (2-sample average) ----
      word r1w = readPiezoAverage2(piezoPin1);
      word r2w = readPiezoAverage2(piezoPin2);

      // Convert to float for EMA math
      float r1 = (float)r1w;
      float r2 = (float)r2w;

      // ---- Update baseline (EMA) ----
      base1 = (1.0f - alpha) * base1 + alpha * r1;
      base2 = (1.0f - alpha) * base2 + alpha * r2;

      // ---- Update noise estimate (EMA of absolute deviation) ----
      float d1 = fabsf(r1 - base1);
      float d2 = fabsf(r2 - base2);
      noise1 = (1.0f - beta) * noise1 + beta * d1;
      noise2 = (1.0f - beta) * noise2 + beta * d2;

      // Enforce a minimum noise floor so thresholds don't collapse to baseline
      float n1 = (noise1 < noise_floor) ? noise_floor : noise1;
      float n2 = (noise2 < noise_floor) ? noise_floor : noise2;

      // ---- Dynamic thresholds ----
      float thr1f = base1 + k * n1;
      float thr2f = base2 + k * n2;

      // ---- Hit tests (increment adders when above dynamic threshold) ----
      // Keep adder as byte; at most 20 increments per 60Hz frame by design
      if (r1 >= thr1f) {
        if (piezo_adder1 < 255) piezo_adder1 += 1;
      }
      if (r2 >= thr2f) {
        if (piezo_adder2 < 255) piezo_adder2 += 1;
      }

      // --- If you ever need to fall back to fixed thresholds, keep these around:
      // if (r1w >= piezo_thres1) { if (piezo_adder1 < 255) piezo_adder1 += 1; }
      // if (r2w >= piezo_thres2) { if (piezo_adder2 < 255) piezo_adder2 += 1; }
    }
  }
}