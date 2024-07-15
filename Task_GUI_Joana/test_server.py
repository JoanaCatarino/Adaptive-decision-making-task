# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 10:50:56 2024

@author: JoanaCatarino
"""
'''
import asyncio
import websockets

connected_clients = set()

async def handler(websocket, path):
    # Register client
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            # Print received message
            print(f"Received message: {message}")

            # Broadcast message to all connected clients
            for client in connected_clients:
                if client != websocket:
                    await client.send(message)
    finally:
        # Unregister client
        connected_clients.remove(websocket)

async def main():
    async with websockets.serve(handler, "10.237.65.85", 8765):
        print("Server started at ws://10.237.65.85:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
'''

import asyncio
import websockets

connected_clients = {}

async def handler(websocket, path):
    # Register client with a unique identifier (for simplicity, using the client's IP)
    client_id = websocket.remote_address[0]
    connected_clients[client_id] = websocket
    print(f"Client {client_id} connected")

    try:
        async for message in websocket:
            # Print received message
            print(f"Received message from {client_id}: {message}")

            # Broadcast message to all connected clients
            await broadcast(message, sender_id=client_id)
    finally:
        # Unregister client
        del connected_clients[client_id]
        print(f"Client {client_id} disconnected")

async def broadcast(message, sender_id=None):
    if connected_clients:
        for client_id, client in connected_clients.items():
            if client_id != sender_id:
                await client.send(message)

async def send_message_to_client(client_id, message):
    if client_id in connected_clients:
        await connected_clients[client_id].send(message)
        print(f"Sent message to {client_id}: {message}")
    else:
        print(f"Client {client_id} not connected")

async def main():
    async with websockets.serve(handler, "10.237.65.85", 8765):
        print("Server started at ws://10.237.65.85:8765")

        # Example: sending a message to a specific client after 10 seconds
        await asyncio.sleep(10)
        await send_message_to_client("specific_client_ip", "Hello, specific client!")

        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
