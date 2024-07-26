# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 19:21:56 2024

@author: JoanaCatarino
"""
'''
import asyncio
import websockets
import json

async def main():
    uri = 'ws://10.237.65.85:8765' # server IP and port 
    print('RPi trying to connect to PC...')
    
    async with websockets.connect(uri) as websocket:
        print ('RPi connected to PC')
        while True:
            packet_from_server = await websocket.recv()
            print('RPi received message from PC:', packet_from_server)
            
            # Now reply to PC that RPi received the message
            reply_packet = 'Confirmation of RPi received:' + packet_from_server
            await websockets.send(reply_packet)
            
            
if __name__ == '__main__':
    asyncio.run(main())

'''

import asyncio
import websockets
from hardware import action_map

async def main():
    uri = 'ws://10.237.65.85:8765' # server IP and port 
    print('RPi trying to connect to PC...')
    
    async with websockets.connect(uri) as websocket:
        print ('RPi connected to PC')
        while True:
            command = await websocket.recv()
            print('RPi received command from PC:', command)
            
            # Execute function based on received command
            if command in action_map:
                await action_map[command]()
            
            # Send a confirmation message back to the server
            reply_message = 'Confirmation of RPi received:' + command
            await websockets.send(command)
            
            
if __name__ == '__main__':
    asyncio.run(main())
    