# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 18:38:00 2024

@author: JoanaCatarino

Generates the 8 and 16KHz pure tones and white noise. How loud the sound is can be regulated with the amplitude variable.
"""

import numpy as np
import pyaudio
import threading

# ===== Audio engine config =====
FS = 48000                   # hardware-friendly samplerate
CHANNELS = 1
FRAMES_PER_BUFFER = 1024
PREFERRED_HINTS = ("hifiberry", "snd_rpi", "soc_sound", "i2s", "bcm")
# ===============================

# Tone generator ---

# For 8KHz tone
def generate_sine_wave_8(frequency, duration, sample_rate=44100, amplitude=0.005): # before amplitude was 0.05 (for speaker with digital gain of 58%)
    t = np.linspace(0, duration, int(sample_rate*duration), endpoint=False)
    wave_8 = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave_8

# For 16KHz tone
def generate_sine_wave_16(frequency, duration, sample_rate=44100, amplitude=0.053): # before amplitude was 0.05 (for speaker with digital gain of 58%)
    t = np.linspace(0, duration, int(sample_rate*duration), endpoint=False)
    wave_16 = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave_16

# For White Noise
def generate_white_noise(duration, sample_rate=44100, amplitude=0.0014): # before amplitude was 0.01
    return np.random.normal(0, amplitude, int(sample_rate*duration))

# ---- Internal audio engine (singleton, thread-safe) ----
_pa = None
_stream = None
_lock = threading.Lock()
_dev_index = None

def _find_dev_index(p):
    """Prefer a HiFiBerry-like device name; otherwise first valid output."""
    hints = tuple(h.lower() for h in PREFERRED_HINTS)
    best = None
    for h in range(p.get_host_api_count()):
        api = p.get_host_api_info_by_index(h)
        for d in range(api['deviceCount']):
            info = p.get_device_info_by_host_api_device_index(h, d)
            if int(info.get('maxOutputChannels', 0)) < 1:
                continue
            name = (info.get('name') or '').lower()
            if any(hint in name for hint in hints):
                return info['index']
            if best is None:
                best = info['index']
    return best

def _ensure_stream():
    """Create PyAudio + one persistent Int16 stream to avoid Pulse timeouts."""
    global _pa, _stream, _dev_index
    if _pa is None:
        _pa = pyaudio.PyAudio()
        try:
            _dev_index = _find_dev_index(_pa)
        except Exception:
            _dev_index = None
    if _stream is None:
        _stream = _pa.open(format=pyaudio.paInt16,
                           channels=CHANNELS,
                           rate=FS,
                           output=True,
                           frames_per_buffer=FRAMES_PER_BUFFER,
                           output_device_index=_dev_index)

def _to_int16(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float32).ravel()
    x = np.clip(x, -1.0, 1.0)
    return (x * 32767).astype(np.int16, copy=False)

def _resample_if_needed(x: np.ndarray, src_rate: int) -> np.ndarray:
    if src_rate == FS or x.size == 0:
        return x.astype(np.float32, copy=False)
    ratio = FS / float(src_rate)
    idx = (np.arange(int(len(x) * ratio)) / ratio).astype(np.float32)
    return np.interp(idx, np.arange(len(x), dtype=np.float32), x).astype(np.float32, copy=False)

# ---- Public API your task uses ----
def play_sound_blocking(sound, sample_rate=44100):
    """Safe from any thread; reuses one Int16 stream; no device index hardcoding."""
    try:
        s = _resample_if_needed(np.asarray(sound, dtype=np.float32).ravel(), sample_rate)
        data = _to_int16(s).tobytes()
        with _lock:
            _ensure_stream()
            _stream.write(data)
    except Exception as e:
        # Avoid crashing your task on audio hiccups; log instead.
        print(f"[AUDIO ERROR] {e}")

def play_sound(sound, sample_rate=44100):
    play_sound_blocking(sound, sample_rate)

def tone_16KHz():
    frequency = 16000
    duration = 0.4
    sr = 44100
    sound = generate_sine_wave_16(frequency, duration, sr)
    play_sound(sound, sr)

def tone_8KHz():
    frequency = 8000
    duration = 0.4
    sr = 44100
    sound = generate_sine_wave_8(frequency, duration, sr)
    play_sound(sound, sr)

def white_noise():
    sr = 44100
    duration = 2
    sound = generate_white_noise(duration, sr)
    play_sound(sound, sr)

# Optional: call at app shutdown
def close_audio():
    global _pa, _stream
    with _lock:
        try:
            if _stream is not None:
                _stream.stop_stream()
                _stream.close()
        finally:
            _stream = None
            if _pa is not None:
                _pa.terminate()
                _pa = None

'''
#Original code - currently working fine for box 1, 3, 4 and ephys

import numpy as np
import pyaudio

# For 8KHz tone
def generate_sine_wave_8(frequency, duration, sample_rate=44100, amplitude=0.005): # before amplitude was 0.05 (for speaker with digital gain of 58%)
    t = np.linspace(0, duration, int(sample_rate*duration), endpoint=False)
    wave_8 = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave_8

# For 16KHz tone
def generate_sine_wave_16(frequency, duration, sample_rate=44100, amplitude=0.053): # before amplitude was 0.05 (for speaker with digital gain of 58%)
    t = np.linspace(0, duration, int(sample_rate*duration), endpoint=False)
    wave_16 = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave_16

# For White Noise
def generate_white_noise(duration, sample_rate=44100, amplitude=0.0014): # before amplitude was 0.01
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

def tone_16KHz():
    frequency = 16000  # frequency in Hz
    duration = 0.4  # Duration in seconds
    sample_rate = 44100  # Sample rate in Hz
    sound = generate_sine_wave_16(frequency, duration, sample_rate)
    play_sound(sound, sample_rate)

def tone_8KHz():
    frequency = 8000  # frequency in Hz
    duration = 0.4  # Duration in seconds
    sample_rate = 44100  # Sample rate in Hz
    sound = generate_sine_wave_8(frequency, duration, sample_rate)
    play_sound(sound, sample_rate)

def white_noise():
    sample_rate = 44100  # Sample rate in Hz
    duration = 2  # Duration in seconds
    sound = generate_white_noise(duration, sample_rate)
    play_sound(sound, sample_rate)
    
'''





