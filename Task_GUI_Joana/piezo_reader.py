# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 16:46:04 2025

@author: JoanaCatarino

piezo reader  - new file just to test the printing of the piezo info
"""


import serial

class PiezoReader:
    def __init__(self):
        self.port = '/dev/ttyACM0'
        self.baudrate = 115200
        self.timeout = 1
        self.packet_size = 6
        self.max_data_points = 180

        self.ser = None  # Serial connection
        self.piezo_adder1 = []
        self.piezo_adder2 = []
        self.buffer = bytearray()
        self.running = True

        # Attempt to set up the serial connection on initialization
        self.setup_serial_connection()

    def setup_serial_connection(self):
        """Set up the serial connection."""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            print(f"Serial connection established on {self.port}")
        except serial.SerialException as e:
            self.ser = None
            print(f"Failed to connect to serial port: {e}")

    def read_serial_data(self):
        """Reads data from the serial port and updates the buffer."""
        if not self.ser or not self.ser.is_open:
            print("Serial connection is not open. Cannot read data.")
            return

        try:
            bytes_to_read = self.packet_size * 10
            self.buffer.extend(self.ser.read(bytes_to_read))

            while len(self.buffer) >= self.packet_size:
                if self.buffer[0] == 0x7F and self.buffer[5] == 0x80:
                    self.piezo_adder1.append(self.buffer[1]* 10) # multiply by 10 to amplify signal
                    self.piezo_adder2.append(self.buffer[3]* 10)
                    
                    if len(self.piezo_adder1) > self.max_data_points:
                        self.piezo_adder1.pop(0)
                    if len(self.piezo_adder2) > self.max_data_points:
                        self.piezo_adder2.pop(0)

                    self.buffer = self.buffer[self.packet_size:]
                else:
                    self.buffer.pop(0)
        except serial.SerialException as e:
            print(f"Serial error: {e}")

    def close_connection(self):
        """Close the serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Serial connection closed.")

