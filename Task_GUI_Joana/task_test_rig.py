# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:32:26 2024

@author: JoanaCatarino

Test rig script
- Start this task should enable the buttons that allow to test different rig components
- All the functions connected to commands related to sound (tones and white noise) should be directly imported
from the sound_generator file.
- Functions to test LEDs (blue and white) are generated here
- Functions to flush water are generated here with some components imported from file x
"""

import threading
import subprocess
from gpio_map import *
from gpiozero import LED
from time import sleep
from sound_generator import tone_16KHz, tone_8KHz, white_noise
from form_updt import Ui_TaskGui

class TestRig:
    def __init__(self, ui):
        self.ui = ui
        self.start()

    def start(self):
        pump_l.on()
        pump_r.on()
        
        print('Test rig starting')

        # Disconnect previous connections to prevent multiple triggers
        self.disconnect_signals()

        # Connect buttons with threaded function calls
        self.ui.chk_16Tone.clicked.connect(self.play_16KHz)
        self.ui.chk_8Tone.clicked.connect(self.play_8KHz)
        self.ui.chk_Punishment.clicked.connect(self.play_white_noise)
        self.ui.chk_BlueLED.clicked.connect(self.toggle_blue_led)
        self.ui.chk_WhiteLED_Left.clicked.connect(self.toggle_white_led_left)
        self.ui.chk_WhiteLED_Right.clicked.connect(self.toggle_white_led_right)
        self.ui.chk_Reward_left.clicked.connect(self.activate_pump_left)
        self.ui.chk_Reward_right.clicked.connect(self.activate_pump_right)
        self.ui.chk_Manip_sound_lights.clicked.connect(self.play_mock_recording)  # Play manipulator sound and flash lights to do a mock recording

    def disconnect_signals(self):
        """ Ensures no duplicate signal connections """
        try:
            self.ui.chk_16Tone.clicked.disconnect()
            self.ui.chk_8Tone.clicked.disconnect()
            self.ui.chk_Punishment.clicked.disconnect()
            self.ui.chk_BlueLED.clicked.disconnect()
            self.ui.chk_WhiteLED_Left.clicked.disconnect()
            self.ui.chk_WhiteLED_Right.clicked.disconnect()
            self.ui.chk_Reward_left.clicked.disconnect()
            self.ui.chk_Reward_right.clicked.disconnect()
            self.ui.chk_Manip_sound_lights.clicked.disconnect()
        except TypeError:
            pass  # If already disconnected, ignore

    ## --- Sound Functions (Threaded) ---
    def play_16KHz(self):
        print("Playing 16KHz Tone")
        threading.Thread(target=tone_16KHz, daemon=True).start()

    def play_8KHz(self):
        print("Playing 8KHz Tone")
        threading.Thread(target=tone_8KHz, daemon=True).start()

    def play_white_noise(self):
        print("Playing White Noise")
        threading.Thread(target=white_noise, daemon=True).start()

    ## --- LED Control ---
    def toggle_blue_led(self):
        print("Toggling Blue LED")
        threading.Thread(target=self.blueLED, daemon=True).start()

    def toggle_white_led_left(self):
        print("Toggling Left White LED")
        threading.Thread(target=self.whiteLLED, daemon=True).start()

    def toggle_white_led_right(self):
        print("Toggling Right White LED")
        threading.Thread(target=self.whiteRLED, daemon=True).start()

    def blueLED(self):
        led_blue.on()
        sleep(1)
        led_blue.off()

    def whiteLLED(self):
        led_white_l.on()
        sleep(1)
        led_white_l.off()

    def whiteRLED(self):
        led_white_r.on()
        sleep(1)
        led_white_r.off()

    ## --- Pump Control ---
    def activate_pump_left(self):
        print("Activating Left Pump")
        threading.Thread(target=self.pumpL, daemon=True).start()

    def activate_pump_right(self):
        print("Activating Right Pump")
        threading.Thread(target=self.pumpR, daemon=True).start()

    def pumpL(self):
        pump_l.off()
        sleep(0.5)
        pump_l.on()

    def pumpR(self):
        pump_r.off()
        sleep(0.5)
        pump_r.on()

    
     ## --- Mock recording: loop sound + alternating lights until Stop pressed ---
    def play_mock_recording(self):
        print("Starting mock recording loop (sound + alternating lights)")

        audio_path = "/home/kmb-box1-raspi/mock_recording_sound/mock_recording_sound.wav"  # <-- change this to your clip path

        # If already running, don't start another set of threads
        if hasattr(self, "mock_stop_event") and self.mock_stop_event is not None and not self.mock_stop_event.is_set():
            print("Mock recording already running")
            return

        self.mock_stop_event = threading.Event()

        def play_audio_loop():
            # Loops the clip until stop is requested
            while not self.mock_stop_event.is_set():
                subprocess.run(["aplay", "-q", audio_path], check=False)

        def alternate_lights_loop():
            # Alternates LEDs until stop is requested
            while not self.mock_stop_event.is_set():
                led_white_l.on()
                led_white_r.off()
                sleep(0.25)
                if self.mock_stop_event.is_set():
                    break

                led_white_l.off()
                led_white_r.on()
                sleep(0.5)

            # Ensure both are off after stopping
            led_white_l.off()
            led_white_r.off()

        threading.Thread(target=play_audio_loop, daemon=True).start()
        threading.Thread(target=alternate_lights_loop, daemon=True).start()
    

    ## --- Stop Function ---
    def stop(self):
        print('Test rig stopping')
        
        # Stop mock recording loop if running
        #if hasattr(self, "mock_stop_event") and self.mock_stop_event is not None:
            #self.mock_stop_event.set()
        
        self.disconnect_signals()




























'''        
class TestRig:
    def __init__(self, ui):
        self.ui = ui
            
        self.start()


    def start(self):
        
        pump_l.on()
        pump_r.on()
        
        print('Test rig starting')
        self.ui.chk_16Tone.clicked.connect(tone_16KHz)
        self.ui.chk_8Tone.clicked.connect(tone_8KHz)
        self.ui.chk_Punishment.clicked.connect(white_noise)
        self.ui.chk_BlueLED.clicked.connect(blueLED)
        self.ui.chk_WhiteLED_Left.clicked.connect(whiteLLED)
        self.ui.chk_WhiteLED_Right.clicked.connect(whiteRLED)
        self.ui.chk_Reward_left.clicked.connect(pumpL)
        self.ui.chk_Reward_right.clicked.connect(pumpR)


        def stop():
            
            print('Test rig stopping')
            
            self.ui.chk_16Tone.clicked.disconnect(tone_16KHz)
            self.ui.chk_8Tone.clicked.disconnect(tone_8KHz)
            self.ui.chk_Punishment.clicked.disconnect(white_noise)
            self.ui.chk_BlueLED.clicked.disconnect(blueLED)            
            self.ui.chk_WhiteLED_Left.clicked.disconnect(whiteLLED)
            self.ui.chk_WhiteLED_Right.clicked.disconnect(whiteRLED)
            self.ui.chk_Reward_left.clicked.disconnect(pumpL)
            self.ui.chk_Reward_right.clicked.disconnect(pumpR)
            
        self.stop = stop


# Test blue LED
def blueLED():
    led_blue.on()
    sleep(1)
    led_blue.off()

# Test white LED on left spout
def whiteLLED():
    led_white_l.on()
    sleep(1)
    led_white_l.off()

# Test white LED on right spout
def whiteRLED():
    led_white_r.on()
    sleep(1)
    led_white_r.off()

# Test white LED on left spout
def pumpL():
    pump_l.off()
    sleep(0.5)
    pump_l.on()

# Test white LED on right spout
def pumpR():
    pump_r.off()
    sleep(0.5)
    pump_r.on()
'''
