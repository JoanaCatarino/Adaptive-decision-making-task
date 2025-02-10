# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 18:38:00 2024

@author: JoanaCatarino
"""

import numpy as np
import pyaudio
import asyncio
from concurrent.futures import ThreadPoolExecutor


def generate_sine_wave(frequency, duration, sample_rate=44100, amplitude=0.5):
    t = np.linspace(0, duration, int(sample_rate*duration), endpoint=False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave

def generate_white_noise(duration, sample_rate=44100, amplitude=0.1):
    samples = np.random.normal(0, amplitude, int(sample_rate*duration))
    return samples

def get_hifiberry_index():
    """Finds the HiFiBerry device index for PyAudio."""
    p = pyaudio.PyAudio()
    device_index = None
    
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if "HiFiBerry" in dev["name"]:  # Adjust this if needed
            device_index = i
            break
    p.terminate()
    
    if device_index is None:
        print("Warning: HiFiBerry not found, using default audio device.")
    return device_index


def play_sound_blocking(sound, sample_rate=44100):
    p = pyaudio.PyAudio()
    device_index = get_hifiberry_index()

    try:
        stream = p.open(format=pyaudio.paFloat32,
                        channels=2,
                        rate=sample_rate,
                        output=True,
                        output_device_index = device_index,
                        frames_per_buffer = 1024)
        stream.write(np.clip(sound, -1.0, 1.0).astype(np.float32).tobytes())
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
   

#def play_sound(sound, sample_rate=44100):
    #asyncio.to_thread(play_sound_blocking, sound, sample_rate)
    

def tone_10KHz():
    frequency = 10000  # frequency in Hz
    duration = 0.2  # Duration in seconds
    sample_rate = 44100  # Sample rate in Hz
    sound = generate_sine_wave(frequency, duration, sample_rate)
    play_sound_blocking(sound)

def tone_5KHz():
    frequency = 5000  # frequency in Hz
    duration = 0.2  # Duration in seconds
    sample_rate = 44100  # Sample rate in Hz
    sound = generate_sine_wave(frequency, duration, sample_rate)
    play_sound_blocking(sound)

def white_noise():
    sample_rate = 44100  # Sample rate in Hz
    duration = 2  # Duration in seconds
    sound = generate_white_noise(duration, sample_rate)
    play_sound_blocking(sound)

if __name__ == '__main__':
    
    tone_10KHz()
    
    tone_5KHz()

    white_noise()
    
'''
# Use this to test the sounds with this script
if __name__ == '__main__':

    tone_10KHz()

    #tone_5KHz()

    #white_noise()
'''


