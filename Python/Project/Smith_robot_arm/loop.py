import tkinter as tk
from tkinter import ttk
import serial
import time

# Initialize serial connection
ser = serial.Serial('COM7', 9600, timeout=1)  # Update COM port as needed

# Function to send angle to Arduino
def set_servo_angle(angle):
    ser.write(f"{angle}\n".encode())

# Function to record movements
def record():
    print("Recording...")
    # Add recording logic

# Function to play back movements
def play():
    print("Playing...")
    # Add playback logic

# Create main window
root = tk.Tk()
root.title("Servo Controller")

# Create widgets
angle_label = ttk.Label(root, text="Angle:")
angle_label.grid(row=0, column=0, padx=10, pady=10)

angle = tk.DoubleVar()
angle_slider = ttk.Scale(root, from_=0, to=180, orient='horizontal', variable=angle)
angle_slider.grid(row=1, column=0, padx=10, pady=10)

record_button = ttk.Button(root, text="Record", command=record)
record_button.grid(row=2, column=0, pady=10)

play_button = ttk.Button(root, text="Play", command=play)
play_button.grid(row=3, column=0, pady=10)

# Function to update servo angle
def update_angle(val):
    angle_value = int(float(val))
    print(f"Setting angle to {angle_value}")
    set_servo_angle(angle_value)

# Bind slider to update function
angle_slider.config(command=lambda val: update_angle(val))

# Start main loop
root.mainloop()
