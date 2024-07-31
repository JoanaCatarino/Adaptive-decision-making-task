# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:47:58 2024

@author: JoanaCatarino
"""
import asyncio
import time

# =============================================================================
# version that works
# async def free_licking():
#     print('Free Licking starting')
#     quiet_window = 0 # pre-defined variable
#     while True:
#         print(f'Quiet window = {quiet_window}')
#         await asyncio.sleep(1)
# =============================================================================

async def free_licking():
    async def start(self):
        print('Free Licking starting')
        quiet_window = 0 # pre-defined variable
        while True:
            print(f'Quiet window = {quiet_window}')
            await asyncio.sleep(1)
        
            async def stop():
                print('Free licking stopping')
                self.stop = stop



# =============================================================================
# 
# class FreeLicking:
#     def start (self):
#         self.send_command_sync('free_licking')
#         print ('Free licking starting')
#         
#         def stop():
#             print ('Free licking stopping')
#         self.stop = stop
#         
# 
# async def free_licking():
#     quiet_window = 0 # defined variable
#     print(quiet_window)
# =============================================================================
        

# =============================================================================
# async def led_blue_action():
#     led_blue.on()
#     await asyncio.sleep(1)
#     led_blue.off() 
# =============================================================================
