# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 15:55:27 2024

@author: JoanaCatarino
"""

import asyncio,websockets
import websockets.exceptions
import json

class Server:
    def __inti__(self, main_controller):
        self.host = '10.237.65.85'
        self.port = 8765
        self.websocket_handle = set()
        self.main_controller = main_controller
        