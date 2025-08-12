# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 16:46:04 2025

@author: JoanaCatarino

piezo reader  - new file just to test the printing of the piezo info
"""

# piezo_reader.py
import serial, threading

class PiezoReader:
    """
    Reads 6-byte frames @ ~60 Hz from Arduino.
    Packet: 0:0x7F, 1:adder1(0..19), 2:first_idx1(0..18 or 255),
            3:adder2(0..19), 4:first_idx2(0..18 or 255), 5:0x80
    """

    def __init__(self, port='/dev/ttyACM0', baudrate=115200, timeout=0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.packet_size = 6

        self.ser = None
        self.buffer = bytearray()

        self.adder1 = []
        self.adder2 = []
        self.idx1   = []
        self.idx2   = []
        self.max_points = 600  # ~10 s history @ 60 Hz

        self._running = False
        self._thread  = None

        self.setup_serial_connection()

    def setup_serial_connection(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            print(f"[PiezoReader] Serial connected on {self.port}")
        except serial.SerialException as e:
            self.ser = None
            print(f"[PiezoReader] Failed to connect: {e}")

    def _append(self, a1, i1, a2, i2):
        self.adder1.append(int(a1)); self.adder2.append(int(a2))
        self.idx1.append(int(i1));   self.idx2.append(int(i2))
        if len(self.adder1) > self.max_points:
            self.adder1.pop(0); self.idx1.pop(0)
        if len(self.adder2) > self.max_points:
            self.adder2.pop(0); self.idx2.pop(0)

    def _read_once(self):
        if not self.ser or not self.ser.is_open:
            return
        # read a few packets worth
        want = self.packet_size * 8
        self.buffer.extend(self.ser.read(want))

        while len(self.buffer) >= self.packet_size:
            if self.buffer[0] == 0x7F and self.buffer[5] == 0x80:
                a1 = self.buffer[1]
                i1 = self.buffer[2]
                a2 = self.buffer[3]
                i2 = self.buffer[4]
                self._append(a1, i1, a2, i2)
                del self.buffer[:self.packet_size]
            else:
                # resync
                self.buffer.pop(0)

    def _pump(self):
        while self._running:
            try:
                self._read_once()
            except serial.SerialException as e:
                print(f"[PiezoReader] Serial error: {e}")
                break
            # no sleep -> keep up with 60 Hz easily

    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._pump, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("[PiezoReader] Serial closed.")

'''
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
                    self.piezo_adder1.append(self.buffer[1]* 500) # multiply by 10 to amplify signal
                    self.piezo_adder2.append(self.buffer[3]* 500)
                    
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
'''
