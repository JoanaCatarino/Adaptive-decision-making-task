
"""
Created on Wed Jul 24 15:20:27 2024

@author: JoanaCatarino
"""

import asyncio, websockets

class Server:
    def __init__(self,task_controller):
        self.host = "10.237.66.177"
        self.port = 8765
        self.websocket_handle = set()
        self.task_controller = task_controller

    async def handler(self, websocket, path):
        # add the websocket to the set for handling outside of the handler
        self.websocket_handle.add(websocket)
        print("RPi client connected.")
        try:
            async for message in websocket:
                # decode packet to utf-8 string
                # message_in = message.decode("utf-8")
                
                # send message to the task controller
                #self.task_controller.received_rpi_message(message)
                print("from RPi: ",message)

        except:
            print("RPi client disconnected.")
        

    async def run(self):
        self.ws_server = await websockets.serve(self.handler, self.host, self.port)
        print("GUI server started...")
