# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 18:38:00 2024

@author: JoanaCatarino

Generates the 8 and 16KHz pure tones and white noise. How loud the sound is can be regulated with the amplitude variable.
"""

# sound_generator.py — ALSA-only playback (no PyAudio)
import numpy as np
import alsaaudio
import threading

# ===== Audio engine config =====
FS = 48000                   # hardware-friendly samplerate
CHANNELS = 1
PERIOD_SIZE = 1024
DEVICE_NAME_HINTS = ("hw:0,0", "default", "plughw:0,0", "sysdefault")

_pcm = None
_lock = threading.Lock()

# ---- Tone generators (unchanged API) ----
def generate_sine_wave_8(frequency, duration, sample_rate=44100, amplitude=0.005):
    t = np.linspace(0, duration, int(sample_rate*duration), endpoint=False)
    return amplitude * np.sin(2 * np.pi * frequency * t)

def generate_sine_wave_16(frequency, duration, sample_rate=44100, amplitude=0.053):
    t = np.linspace(0, duration, int(sample_rate*duration), endpoint=False)
    return amplitude * np.sin(2 * np.pi * frequency * t)

def generate_white_noise(duration, sample_rate=44100, amplitude=0.0014):
    return np.random.normal(0, amplitude, int(sample_rate*duration))

# ---- ALSA helpers ----
def _ensure_pcm():
    """Create one persistent ALSA PCM handle (exclusive), Int16 @ 48k."""
    global _pcm
    if _pcm is not None:
        return

    # Try a few common device names; hw:0,0 is often HiFiBerry if it's card 0.
    last_err = None
    for name in DEVICE_NAME_HINTS:
        try:
            pcm = alsaaudio.PCM(type=alsaaudio.PCM_PLAYBACK, mode=alsaaudio.PCM_NORMAL, device=name)
            pcm.setchannels(CHANNELS)
            pcm.setrate(FS)
            pcm.setformat(alsaaudio.PCM_FORMAT_S16_LE)
            pcm.setperiodsize(PERIOD_SIZE)
            _pcm = pcm
            # print(f"[ALSA] using device {name}")  # optional debug
            return
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"Could not open ALSA playback device: {last_err}")

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
    """Safe from any thread; reuses one ALSA PCM; no Pulse/PortAudio involved."""
    try:
        s = _resample_if_needed(np.asarray(sound, dtype=np.float32).ravel(), sample_rate)
        data = _to_int16(s).tobytes()
        with _lock:
            _ensure_pcm()
            # Write in chunks the size ALSA expects
            for i in range(0, len(data), PERIOD_SIZE * 2):  # 2 bytes per int16 sample
                _pcm.write(data[i:i + PERIOD_SIZE * 2])
    except Exception as e:
        print(f"[ALSA AUDIO ERROR] {e}")

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

def close_audio():
    global _pcm
    with _lock:
        if _pcm is not None:
            try:
                _pcm.drain()
            except Exception:
                pass
            _pcm = None
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





