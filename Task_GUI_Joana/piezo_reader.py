# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 16:46:04 2025

@author: JoanaCatarino

piezo reader  - new file just to test the printing of the piezo info
"""

import serial
import threading

class PiezoReader:
    def __init__(self):
        self.ser = None
        self.packet_size = 6
        self.max_data_points = 600
        self.piezo_adder1 = []
        self.piezo_adder2 = []
        self.buffer = bytearray()
        self.running = True

    def setup_serial_connection(self):
        self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

    def read_serial_data(self):
        try:
            bytes_to_read = self.packet_size * 10
            while self.running:
                self.buffer.extend(self.ser.read(bytes_to_read))
                while len(self.buffer) >= self.packet_size:
                    if self.buffer[0] == 0x7F and self.buffer[5] == 0x80:
                        self.piezo_adder1.append(self.buffer[1])
                        self.piezo_adder2.append(self.buffer[3])
                        if len(self.piezo_adder1) > self.max_data_points:
                            self.piezo_adder1.pop(0)
                        if len(self.piezo_adder2) > self.max_data_points:
                            self.piezo_adder2.pop(0)
                        self.buffer = self.buffer[self.packet_size:]
                    else:
                        self.buffer.pop(0)
        except serial.SerialException as e:
            print(f"Serial error: {e}")

    def start_reading(self):
        threading.Thread(target=self.read_serial_data, daemon=True).start()

    def stop(self):
        self.running = False
        if self.ser:
            self.ser.close()
