# -*- coding: utf-8 -*-
"""
Created on Mon May  5 18:24:27 2025

@author: JoanaCatarino
"""

import cv2 
 
cap = cv2.VideoCapture(0, cv2.CAP_V4L2) 
if not cap.isOpened(): 
    print("Camera not accessible") 
    exit() 
 
# Set desired window size 
desired_width = 400 
desired_height = 230 
 
while True: 
    ret, frame = cap.read() 
    if not ret: 
        print("Failed to grab frame") 
        break 
 
    resized_frame = cv2.resize(frame, (desired_width, desired_height)) 
    cv2.imshow("Camera", resized_frame) 
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break 
 
cap.release() 
cv2.destroyAllWindows()