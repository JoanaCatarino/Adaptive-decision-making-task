# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 18:38:00 2024

@author: JoanaCatarino
"""

import numpy as np
import pyaudio
import asyncio
from concurrent.futures import ThreadPoolExecutor

# A thread pool for running blocking operations
executor = ThreadPoolExecutor()

def generate_sine_wave(frequency, duration, sample_rate=44100, amplitude=0.5):
    t = np.linspace(0, duration, int(sample_rate*duration), endpoint=False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave

def generate_white_noise(duration, sample_rate=44100, amplitude=0.1):
    samples = np.random.normal(0, amplitude, int(sample_rate*duration))
    return samples

def play_sound_blocking(sound, sample_rate=44100):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=sample_rate,
                    output=True)
    stream.write(sound.astype(np.float32).tobytes())
    stream.stop_stream()
    stream.close()
    p.terminate()

def play_sound(sound, sample_rate=44100):
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, play_sound_blocking, sound, sample_rate)

def tone_10KHz():
    frequency = 10000  # frequency in Hz
    duration = 0.2  # Duration in seconds
    sample_rate = 44100  # Sample rate in Hz
    sound = generate_sine_wave(frequency, duration, sample_rate)
    play_sound(sound, sample_rate)

def tone_5KHz():
    frequency = 5000  # frequency in Hz
    duration = 0.2  # Duration in seconds
    sample_rate = 44100  # Sample rate in Hz
    sound = generate_sine_wave(frequency, duration, sample_rate)
    play_sound(sound, sample_rate)

def white_noise():
    sample_rate = 44100  # Sample rate in Hz
    duration = 2  # Duration in seconds
    sound = generate_white_noise(duration, sample_rate)
    play_sound(sound, sample_rate)

if __name__ == '__main__':
    # To test the sounds asynchronously
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(white_noise())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


'''
# Use this to test the sounds with this script
if __name__ == '__main__':

    tone_10KHz()

    #tone_5KHz()

    #white_noise()
'''


