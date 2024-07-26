# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 19:21:56 2024

@author: JoanaCatarino
"""

import asyncio
import websockets
from hardware import FunctionMap

async def main():
    # Initiate FunctionMap
    func_map = FunctionMap()
    
    uri = 'ws://10.237.66.177:8765' # server IP and port 
    print('RPi trying to connect to PC...')
    
    async with websockets.connect(uri) as websocket:
        print ('RPi connected to PC')
        while True:
            command = await websocket.recv()
            print('RPi received command from PC:', command)
            
            # Execute command funtions with the same name
            getattr(func_map, command)()

           
            
if __name__ == '__main__':
    asyncio.run(main())
    