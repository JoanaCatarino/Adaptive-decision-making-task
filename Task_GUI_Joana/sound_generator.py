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

def generate_white_noise(frequency, sample_rate=44100, amplitude=0.5):
    # Generate white noise
    samples = np.random.normal(0, amplitude, int(sample_rate*duration))
    return samples

