# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 18:38:00 2024

@author: JoanaCatarino

Generates the 5 and 10KHz pure tones and white noise. How loud the sound is can be regulated with the amplitude variable.
"""

import numpy as np
import pyaudio

# For 5KHz tone
def generate_sine_wave_5(frequency, duration, sample_rate=44100, amplitude=0.0003): # before amplitude was 0.05 (for speaker with digital gain of 58%)
    t = np.linspace(0, duration, int(sample_rate*duration), endpoint=False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave_5

# For 10KHz tone
def generate_sine_wave_10(frequency, duration, sample_rate=44100, amplitude=0.0003): # before amplitude was 0.05 (for speaker with digital gain of 58%)
    t = np.linspace(0, duration, int(sample_rate*duration), endpoint=False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave_10

# For White Noise
def generate_white_noise(duration, sample_rate=44100, amplitude=0.0001): # before amplitude was 0.01
    return np.random.normal(0, amplitude, int(sample_rate*duration))

def play_sound_blocking(sound, sample_rate=44100):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=sample_rate,
                    output=True,
                    output_device_index=0)
    stream.write(sound.astype(np.float32).tobytes())
    stream.stop_stream()
    stream.close()
    p.terminate()

def play_sound(sound, sample_rate=44100):
    play_sound_blocking(sound, sample_rate)

def tone_10KHz():
    frequency = 10000  # frequency in Hz
    duration = 0.2  # Duration in seconds
    sample_rate = 44100  # Sample rate in Hz
    sound = generate_sine_wave_10(frequency, duration, sample_rate)
    play_sound(sound, sample_rate)

def tone_5KHz():
    frequency = 5000  # frequency in Hz
    duration = 0.2  # Duration in seconds
    sample_rate = 44100  # Sample rate in Hz
    sound = generate_sine_wave_5(frequency, duration, sample_rate)
    play_sound(sound, sample_rate)

def white_noise():
    sample_rate = 44100  # Sample rate in Hz
    duration = 2  # Duration in seconds
    sound = generate_white_noise(duration, sample_rate)
    play_sound(sound, sample_rate)




