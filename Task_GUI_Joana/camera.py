import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt

def start_camera(cap, timer, update_frame_slot):
    # Open the video capture
    cap.open(0)  # 0 for the default USB camera
    if not cap.isOpened():
        print("Error: Camera not accessible")
        return
    # Start the timer to capture frames
    timer.timeout.connect(update_frame_slot)
    timer.start(10)  # Capture a frame every 30ms (~33fps)

def stop_camera(cap, label, ov_label):
    # Check if the camera is opened and release it
    if cap.isOpened():
        cap.release()
    # Clear the QLabel to remove the current pixmap for both Gui and Overview tab
    label.clear()
    ov_label.clear()

def update_frame(cap, label, ov_label):
    # Capture a frame from the camera
    ret, frame = cap.read()
    if ret:
        # Convert the frame to RGB format (as OpenCV uses BGR)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convert the frame to QImage
        height, width, channel = frame_rgb.shape
        bytes_per_line = 3 * width
        qimg = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
        # Set the image to the QLabel and scale it to fit
        pixmap = QPixmap.fromImage(qimg)
        label.setPixmap(pixmap.scaled(label.size(), aspectRatioMode=Qt.IgnoreAspectRatio))
        # Update the QLabel in the Overview tab
        ov_label.setPixmap(pixmap.scaled(ov_label.size(), aspectRatioMode=Qt.IgnoreAspectRatio))