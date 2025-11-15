Gesture Controlled Virtual Mouse

This project allows you to control your computer's mouse using hand gestures captured through your webcam. It uses Python with OpenCV for video processing and MediaPipe for advanced hand landmark detection.

Features

Smooth Cursor Movement: Control the cursor by moving your hand.

Cursor Pause: Temporarily lock the cursor to perform precise gestures without moving it, similar to lifting your finger off a trackpad.

Clicking: Perform left, right, and double clicks.

Dragging: Select and move items with a fist gesture.

Scrolling: Scroll vertically by pinching and moving your hand.

System Actions: Take screenshots, perform copy, cut, paste actions, and stop the application.

Visual Feedback: The application window shows your hand with landmarks and displays the current action being performed.

Prerequisites

Python Version

It is highly recommended to use Python 3.10. While it may work on other 3.x versions, 3.10 has proven compatibility with all the required libraries.

Required Libraries

You need to install the necessary Python packages. You can do this easily using the provided requirements.txt file.

Setup and Installation

Clone or download the repository.

Create a virtual environment (Recommended):

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`


Install the dependencies:

pip install -r requirements.txt


How to Run

Simply execute the main Python script from your terminal:

python virtual_mouse.py


A window will appear showing your webcam feed. Your hand gestures will now control the mouse. To stop the program, press the 'q' key or use the stop gesture.

Gesture Guide

Here is a list of all the gestures and the actions they perform:

Gesture

Action

Index & Middle Finger Up

Move Cursor (follows index finger tip)

Index, Middle Finger & Thumb Up

Pause Cursor (stops mouse movement)

Pinch Index Finger & Thumb

Left Click

Pinch Middle Finger & Thumb

Right Click

Pinch Ring Finger & Thumb

Double Click

Pinch Index Finger & Thumb (move hand up/down)

Scroll Vertically

Make a Fist

Select/Hold Item

Make a Fist and Move Hand

Drag and Drop

Only Thumb Up

Take Screenshot (saved in project dir)

Four Fingers Up (Index, Middle, Ring, Pinky)

Copy (Ctrl+C)

Scissor Gesture (Index & Middle finger spread)

Cut (Ctrl+X)

Scissor Gesture (after a Copy gesture)

Paste (Ctrl+V)

Open Palm (All 5 fingers up)

Stop Application

