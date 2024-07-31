# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:47:58 2024

@author: JoanaCatarino
"""
import asyncio


class FreeLicking:
    def start (self):
        print ('Free licking starting')
        def stop():
            print ('Free licking stopping')
        self.stop = stop
        

async def free_licking():
    quiet_window = 0 # defined variable
    while True:
        print(quiet_window)
        await asyncio.sleep(1)  # Sleep for 1 second
        

# =============================================================================
# async def led_blue_action():
#     led_blue.on()
#     await asyncio.sleep(1)
#     led_blue.off() 
# =============================================================================
