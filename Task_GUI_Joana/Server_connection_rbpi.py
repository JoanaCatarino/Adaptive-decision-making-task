# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 17:25:15 2024

@author: JoanaCatarino
"""
'''
import asyncio
import websockets

async def handler(websocket, path):
    async for message in websocket:
        print(f"Received message from client: {message}")
        # Echo the message back to the client
        await websocket.send(f"Server received: {message}")

async def main():
    async with websockets.serve(handler, "10.237.65.85", 8765):
        print("WebSocket server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        # Check if there's an existing event loop
        loop = asyncio.get_running_loop()
    except RuntimeError:  # No event loop is currently running
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    else:
        # If an event loop is already running, start the server using it
        loop.create_task(main())
        loop.run_forever()
'''
'''
import asyncio
import websockets

# Global variable to store the WebSocket server instance
server = None

async def handler(websocket, path):
    try:
        async for message in websocket:
            print(f"Received message from client: {message}")
            # Echo the message back to the client
            await websocket.send(f"Server received: {message}")
    except websockets.ConnectionClosed:
        pass

async def start_server():
    global server
    server = await websockets.serve(handler, "10.237.65.85", 8765)
    print("WebSocket server started on ws://10.237.65.85:8765")

    try:
        await asyncio.Future()  # Run forever
    except asyncio.CancelledError:
        pass
    finally:
        if server:
            server.close()
            await server.wait_closed()
            print("WebSocket server closed")

def run_server():
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(start_server())
        loop.run_forever()
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Closing server...")
        if server:
            asyncio.run_coroutine_threadsafe(server.close(), loop)
    finally:
        loop.close()

if __name__ == "__main__":
    run_server()
'''
import asyncio
import websockets

async def handler(websocket, path):
    try:
        async for message in websocket:
            print(f"Received message from client: {message}")
            if message.strip().lower() == 'quit':
                await websocket.send("Server is shutting down. Goodbye!")
                await websocket.close()
                print(f"Client {websocket.remote_address} disconnected")
                return  # Exit the handler if client sends 'quit'
            await websocket.send(f"Server received: {message}")
    except websockets.ConnectionClosed:
        pass

async def start_server():
    server = await websockets.serve(handler, "10.237.65.85", 8765)
    print("WebSocket server started on ws://10.237.65.85:8765")

    try:
        await asyncio.Future()  # Run forever
    except asyncio.CancelledError:
        pass
    finally:
        server.close()
        await server.wait_closed()
        print("WebSocket server closed")

def run_server():
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(start_server())
        loop.run_forever()
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Closing server...")
        loop.stop()  # Stop the event loop
    finally:
        loop.close()

if __name__ == "__main__":
    run_server()

