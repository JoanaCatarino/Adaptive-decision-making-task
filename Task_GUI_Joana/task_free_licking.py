# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:47:58 2024

@author: JoanaCatarino
"""
import time
from threading import Thread

class FreeLicking:
    def __init__(self):
        self._is_running = False
        self._thread = None

    def start(self):
        print('Free licking starting')
        self._is_running = True
        self._thread = Thread(target=self.free_licking)
        self._thread.start()

    def stop(self):
        print('Free licking stopping')
        self._is_running = False
        if self._thread:
            self._thread.join()  # Wait for the thread to finish

    def free_licking(self):
        quiet_window = 0
        while self._is_running:
            print(quiet_window)
            time.sleep(1)  # Sleep for 1 second