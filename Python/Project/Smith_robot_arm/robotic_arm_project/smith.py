import cv2
import numpy as np
import serial
import threading
import speech_recognition as sr
import tkinter as tk
from tkinter import ttk

# Set up the serial connection to the Arduino
arduino_port = 'COM7'  # Change this to your Arduino's port
baud_rate = 9600

try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")

# Define the classes and their color ranges in HSV
color_ranges = {
    "Handle": ((25, 50, 50), (35, 255, 255)),  # Example HSV range for yellow
    "Forceps": ((100, 150, 0), (140, 255, 255)),  # Example HSV range for blue
    "IrisScissors": ((0, 70, 50), (10, 255, 255)),  # Example HSV range for red
    "MetzenbaumScissors": ((50, 100, 100), (70, 255, 255))  # Example HSV range for green
}

# Define colors for drawing
draw_colors = {
    "Handle": (0, 255, 255),  # Yellow
    "Forceps": (255, 0, 0),  # Blue
    "IrisScissors": (0, 0, 255),  # Red
    "MetzenbaumScissors": (0, 255, 0)  # Green
}

def send_command(command):
    if ser.is_open:
        ser.write((command + '\n').encode())
    else:
        print("Serial port is not open.")

def detect_instruments(frame):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    detected_instruments = []

    for instrument, (lower, upper) in color_ranges.items():
        mask = cv2.inRange(hsv_frame, np.array(lower), np.array(upper))
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            if cv2.contourArea(contour) > 500:  # Minimum area threshold
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), draw_colors[instrument], 2)
                cv2.putText(frame, instrument, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, draw_colors[instrument], 2)
                detected_instruments.append(instrument)

    return detected_instruments

def start_detection():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        instruments = detect_instruments(frame)
        
        cv2.putText(frame, "Mode: Automatic Detection", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Instrument Detection', frame)
        if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
            break
    cap.release()
    cv2.destroyAllWindows()

def voice_control():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for commands...")
        while True:
            try:
                audio = recognizer.listen(source, timeout=5)
                command = recognizer.recognize_google(audio).lower()
                print(f"Command received: {command}")
                
                # Map voice commands to actions
                if "pick up" in command:
                    for instrument in color_ranges.keys():
                        if instrument.lower() in command:
                            send_command(instrument)
                            print(f"Picking up {instrument}")
                            break
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")

def on_submit():
    if mode_var.get() == "Automatic":
        threading.Thread(target=start_detection).start()
        threading.Thread(target=voice_control).start()

def update_mode():
    if mode_var.get() == "Automatic":
        submit_button.config(state="normal")
        manual_frame.pack_forget()
    else:
        submit_button.config(state="disabled")
        manual_frame.pack(pady=10)

def update_servo(servo, angle):
    command = f"Servo{servo}:{angle}"
    threading.Thread(target=send_command, args=(command,)).start()
    degree_labels[servo].config(text=f"{int(float(angle))}°")

# GUI setup
root = tk.Tk()
root.title("Robotic Arm Control")

mode_var = tk.StringVar(value="Automatic")

ttk.Label(root, text="Control Mode:").pack(pady=10)
ttk.Radiobutton(root, text="Automatic Detection", variable=mode_var, value="Automatic", command=update_mode).pack()
ttk.Radiobutton(root, text="Manual Control", variable=mode_var, value="Manual", command=update_mode).pack()

submit_button = ttk.Button(root, text="Submit", command=on_submit)
submit_button.pack(pady=10)

# Manual control frame
manual_frame = ttk.Frame(root)

servo_labels = ["Servo 1", "Servo 2", "Servo 3", "Servo 4", "Servo 5"]
servo_sliders = []
degree_labels = []

for i, label in enumerate(servo_labels):
    frame = ttk.Frame(manual_frame)
    frame.pack(pady=5)
    
    ttk.Label(frame, text=label).pack(side=tk.LEFT)
    
    slider = ttk.Scale(frame, from_=0, to=180, orient='horizontal', command=lambda angle, s=i: update_servo(s, angle))
    slider.pack(side=tk.LEFT, padx=5)
    
    degree_label = ttk.Label(frame, text="0°")
    degree_label.pack(side=tk.LEFT)
    
    servo_sliders.append(slider)
    degree_labels.append(degree_label)

update_mode()

root.mainloop()
