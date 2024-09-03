import cv2
import numpy as np
import serial
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import speech_recognition as sr

# Set up the serial connection to the Arduino
arduino_port = '/dev/ttyUSB0'  # Change this to your Arduino's port
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

# Flags for detection and command
detection_active = False
follow_command_active = False
active_device = None

# Store the initial positions for each servo
initial_servo_positions = [90, 0, 110, 0, 0, 0]  # Set each servo to 90 degrees as an example

# Threads
camera_thread = None
voice_thread = None

# Control flags
camera_running = False
voice_running = False

def send_command(command):
    if ser.is_open:
        ser.write((command + '\n').encode())
    else:
        print("Serial port is not open.")

def detect_and_display(frame):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    detected_instruments = []

    for device, (lower, upper) in color_ranges.items():
        mask = cv2.inRange(hsv_frame, np.array(lower), np.array(upper))
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            if cv2.contourArea(contour) > 500:  # Minimum area threshold
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), draw_colors[device], 2)
                cv2.putText(frame, device, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, draw_colors[device], 2)
                detected_instruments.append((device, x + w // 2, y + h // 2))

    # Display detected device names in the upper left corner
    if detected_instruments:
        detected_names = [instr[0] for instr in detected_instruments]
        detected_text = "Detected: " + ", ".join(set(detected_names))
        cv2.putText(frame, detected_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    return detected_instruments

def follow_instrument(instrument, x, y):
    # Only control servo 0 (base servo)
    servo_x = int((x / 640) * 180)  # Map x position to servo angle for servo 0

    command = f"Servo0:{servo_x}"
    print(f"Following {instrument}: {command}")
    send_command(command)

def start_camera():
    global camera_running
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    camera_running = True
    while camera_running:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        detected_instruments = detect_and_display(frame)
        if follow_command_active and active_device:
            for instrument, x, y in detected_instruments:
                if instrument == active_device:
                    follow_instrument(instrument, x, y)

        # Convert the image from OpenCV BGR format to RGB format
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)

        camera_label.imgtk = imgtk
        camera_label.configure(image=imgtk)

    cap.release()
    camera_label.config(image='')

def stop_camera():
    global camera_running
    camera_running = False

def voice_control():
    global voice_running
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    voice_running = True
    while voice_running:
        with microphone as source:
            print("Listening for commands...")
            audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"Voice command received: {command}")

            global follow_command_active, active_device

            if "track handle" in command:
                follow_command_active = True
                active_device = "Handle"
                print("Tracking Handle.")

            elif "track forceps" in command:
                follow_command_active = True
                active_device = "Forceps"
                print("Tracking Forceps.")

            elif "track iris scissors" in command:
                follow_command_active = True
                active_device = "IrisScissors"
                print("Tracking Iris Scissors.")

            elif "track metzenbaum scissors" in command:
                follow_command_active = True
                active_device = "MetzenbaumScissors"
                print("Tracking Metzenbaum Scissors.")

            elif "stop tracking" in command:
                follow_command_active = False
                print("Following deactivated.")

        except sr.UnknownValueError:
            print("Could not understand the audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

def stop_voice_control():
    global voice_running
    voice_running = False

def update_servo(servo, angle):
    initial_servo_positions[servo] = angle  # Update the initial position
    command = f"Servo{servo}:{angle}"
    print(f"Sending command: {command}")
    threading.Thread(target=send_command, args=(command,)).start()
    degree_labels[servo].config(text=f"{int(float(angle))}°")

def send_initial_servo_positions():
    for i, angle in enumerate(initial_servo_positions):
        command = f"Servo{i}:{angle}"
        print(f"Sending initial command: {command}")
        send_command(command)

def confirm_mode():
    selected_mode = mode_var.get()
    if selected_mode == "Automatic":
        # Hide manual controls when in Automatic mode
        manual_frame.pack_forget()

        # Move all servos to their initial set positions
        for i, angle in enumerate(initial_servo_positions):
            update_servo(i, angle)
            sliders[i].set(angle)
            angle_entries[i].delete(0, tk.END)
            angle_entries[i].insert(0, str(angle))

        # Start the camera and voice control threads
        global camera_thread, voice_thread
        camera_thread = threading.Thread(target=start_camera)
        voice_thread = threading.Thread(target=voice_control)
        camera_thread.start()
        voice_thread.start()
    else:
        # Show manual controls when in Manual mode
        manual_frame.pack(pady=10)
        
        # Stop the camera and voice control when switching to manual mode
        stop_camera()
        stop_voice_control()
        print("Switched to Manual Mode")

def move_servo(servo_index):
    try:
        angle = int(angle_entries[servo_index].get())
        if 0 <= angle <= 180:
            sliders[servo_index].set(angle)
            update_servo(servo_index, angle)
        else:
            print("Angle out of range. Please enter a value between 0 and 180.")
    except ValueError:
        print("Invalid input. Please enter a valid integer.")

def update_degree_label(val, servo_index):
    degree_labels[servo_index].config(text=f"{int(float(val))}°")
    angle_entries[servo_index].delete(0, tk.END)
    angle_entries[servo_index].insert(0, str(int(float(val))))

# GUI setup
root = tk.Tk()
root.title("Robotic Arm Control")

mode_var = tk.StringVar(value="Manual")

mode_label = ttk.Label(root, text="Mode:")
mode_label.pack(pady=10)

mode_combobox = ttk.Combobox(root, textvariable=mode_var, values=["Manual", "Automatic"])
mode_combobox.pack(pady=10)

submit_button = ttk.Button(root, text="Submit", command=confirm_mode)
submit_button.pack(pady=10)

manual_frame = tk.Frame(root)

sliders = []
degree_labels = []
angle_entries = []

for i in range(6):  # Assuming 6 servos
    frame = tk.Frame(manual_frame)
    frame.pack(pady=5)

    label = ttk.Label(frame, text=f"Servo {i}:")
    label.pack(side=tk.LEFT, padx=5)

    slider = ttk.Scale(frame, from_=0, to=180, orient=tk.HORIZONTAL, command=lambda val, i=i: update_degree_label(val, i))
    slider.set(initial_servo_positions[i])  # Initialize slider to the initial position
    slider.pack(side=tk.LEFT, padx=5)
    sliders.append(slider)

    degree_label = ttk.Label(frame, text=f"{initial_servo_positions[i]}°")  # Initialize degree label to the initial position
    degree_label.pack(side=tk.LEFT, padx=5)
    degree_labels.append(degree_label)

    angle_entry = ttk.Entry(frame, width=5)
    angle_entry.insert(0, str(initial_servo_positions[i]))  # Initialize entry to the initial position
    angle_entry.pack(side=tk.LEFT, padx=5)
    angle_entries.append(angle_entry)

    move_button = ttk.Button(frame, text="Move", command=lambda i=i: move_servo(i))
    move_button.pack(side=tk.LEFT, padx=5)

manual_frame.pack(pady=10)

# Add a label to display the camera feed
camera_label = tk.Label(root)
camera_label.pack()

# Send initial servo positions at startup
send_initial_servo_positions()

# Start the Tkinter main loop
root.mainloop()
