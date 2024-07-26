
"""
Created on Wed Jul 24 15:20:27 2024

@author: JoanaCatarino
"""
'''
import asyncio
import websockets

client_connected_event = asyncio.Event()

# Start the WebSocket server
async def start_server():
    print("Started server")
    async with websockets.serve(handler, "10.237.66.177", 8765):
        await asyncio.Future()  # Run forever
    print("WebSocket ended")

# Listen for user input and send messages to connected clients
async def listen_for_input(): 
    await client_connected_event.wait()  # Wait until a client is connected
    loop = asyncio.get_event_loop()
    while True:
        user_input = await loop.run_in_executor(None, input, "Enter message to send: ")
        # Logic to broadcast the message to all connected clients
        for ws in connected_clients:
            await ws.send(user_input)

# Main function to start the server and input listener
async def main():
    # Set up the server task
    server_task = asyncio.create_task(start_server())
    
    # Set up the input listener task
    input_task = asyncio.create_task(listen_for_input())
    
    # Run both tasks concurrently
    await asyncio.gather(server_task, input_task)

# List to hold connected WebSocket clients
connected_clients = set()

# Register WebSocket client connections
async def handler(websocket, path):
    connected_clients.add(websocket)
    print("RPi client connected.")
    client_connected_event.set()  # Signal that a client has connected
    try:
        async for message in websocket:
            print("Received reply from RPi: ", message)
    except websockets.exceptions.ConnectionClosedOK:
        print("RPi client disconnected.")
    except websockets.exceptions.ConnectionClosedError:
        print("RPi client disconnected.")
    finally:
        connected_clients.remove(websocket)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server interrupted by user")
        
'''


import asyncio
import websockets

client_connected_event = asyncio.Event()

# Start the WebSocket server
async def start_server():
    print("Started server")
    port = 8765
    while True:
        try:
            async with websockets.serve(handler, "10.237.66.177", port):
                print(f'server started on port {port}')
                await asyncio.Future()  # Run forever
                
        except OSError as e:
            if e.errno == 10048: #Port already in use
                print(f'Port {port} is already in use, trying next port')
                port += 1
            else:
                raise
    print("WebSocket ended")

# Listen for user input and send messages to connected clients
async def listen_for_input(): 
    await client_connected_event.wait()  # Wait until a client is connected
    loop = asyncio.get_event_loop()
    while True:
        user_input = await loop.run_in_executor(None, input, "Enter message to send: ")
        # Logic to broadcast the message to all connected clients
        for ws in connected_clients:
            await ws.send(user_input)

# Main function to start the server and input listener
async def main():
    # Set up the server task
    server_task = asyncio.create_task(start_server())
    
    # Set up the input listener task
    input_task = asyncio.create_task(listen_for_input())
    
    # Run both tasks concurrently
    await asyncio.gather(server_task, input_task)

# List to hold connected WebSocket clients
connected_clients = set()

# Register WebSocket client connections
async def handler(websocket, path):
    connected_clients.add(websocket)
    print("RPi client connected.")
    client_connected_event.set()  # Signal that a client has connected
    try:
        async for message in websocket:
            print("Received reply from RPi: ", message)
    except websockets.exceptions.ConnectionClosedOK:
        print("RPi client disconnected.")
    except websockets.exceptions.ConnectionClosedError:
        print("RPi client disconnected.")
    finally:
        connected_clients.remove(websocket)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server interrupted by user")