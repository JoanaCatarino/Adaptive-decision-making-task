# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 18:42:29 2024

@author: JoanaCatarino
"""

import asyncio
import websockets

async def send_receive():
    uri = "ws://<10.237.65.85>:8765"  # Replace <PC_IP_ADDRESS> with the actual IP address of your PC
    async with websockets.connect(uri) as websocket:
        try:
            while True:
                message = input("Enter message to send (or 'quit' to disconnect):")
                await websocket.send(message)
                if message == 'quit':
                    print('Disconnecting...')
                    await websocket.close()
                    print ('Connection closed')
                    break
                response = await websocket.recv()
                print(f"Received message from server: {response}")
        except websockets.ConnectionClosed:
            print('Connection sloded by server')
        except Exception as e:
            print(f'An error occurred:{e}')
            


if __name__ == "__main__":
    try:
        asyncio.run(send_receive())
    except RuntimeError as e:
        if str(e) == 'This event loop is already running'
            loop = asyncio.get_event_loop()
            loop.run_until_complete(send_receive())
        else:
            raise
            