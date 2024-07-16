# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 18:38:00 2024

@author: JoanaCatarino
"""
import numpy as np
import pyaudio

def generate_sine_wave(frequency, duration, sample_rate=44100, amplitude=0.5):
    t = np.linspace(0, duration, int(sample_rate*duration), endpoint=False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave

def generate_white_noise(duration, sample_rate=44100, amplitude=0.2): # This amplitude will control how loud the noise is
    # Generate white noise
    samples = np.random.normal(0, amplitude, int(sample_rate*duration))
    return samples

def play_sound(sound, sample_rate=44100):
    p = pyaudio.PyAudio()
    stream = p.open(format = pyaudio.paFloat32,
                    channels = 1,
                    rate = sample_rate,
                    output = True)
    stream.write(sound.astype(np.float32).tobytes())
    stream.stop_stream()
    stream.close()
    p.terminate()
    
def tone_10KHz():
    frequency = 10000 # frequency in Hz
    duration = 0.2 # Duraton in seconds
    sample_rate = 44100 # Sample rate in Hz
    sound = generate_sine_wave(frequency, duration, sample_rate)
    play_sound(sound, sample_rate)
    
def tone_5KHz():
    frequency = 5000 # frequency in Hz
    duration = 0.2 # Duraton in seconds
    sample_rate = 44100 # Sample rate in Hz
    sound = generate_sine_wave(frequency, duration, sample_rate)
    play_sound(sound, sample_rate)
    
def white_noise():
    sample_rate = 44100 # Sample rate in Hz
    duration = 2 # Duration in seconds
    sound = generate_white_noise(duration, sample_rate)
    play_sound(sound, sample_rate)

'''    
# Use this to test the sounds with this script  
if __name__ == '__main__':
   
    #tone_10KHz()
    
    #tone_5KHz()
    
    white_noise()
'''  
    
    
    
    