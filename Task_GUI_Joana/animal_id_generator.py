# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 17:44:52 2024

@author: JoanaCatarino
"""

import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox

# Create the main application instance
app = QApplication(sys.argv)

# Create a QWidget as the main window
widget = QWidget()

# Create a QVBoxLayout to arrange widgets vertically
layout = QVBoxLayout(widget)

# Create a QComboBox and add it to the layout
combo_box = QComboBox()
layout.addWidget(combo_box)

# Add items to the QComboBox
combo_box.addItem("Item 1")
combo_box.addItem("Item 2")
combo_box.addItem("Item 3")

# Optionally, you can add items dynamically from a list or other iterable
items = ["Apple", "Banana", "Orange", "Grapes"]
for item in items:
    combo_box.addItem(item)

# Show the widget
widget.setLayout(layout)
widget.show()

# Execute the application's main loop
sys.exit(app.exec())
