import tkinter as tk
from arduino_comm import send_command
from voice_control import start_voice_control

def on_slider_change(val):
    value = float(val)
    if value < 50:
        print("Voice Control Mode:", value)
        start_voice_control(value)  # Pass sensitivity to voice control
    else:
        print("Manual Control Mode:", value)
        # Implement manual control logic here (e.g., map slider to servo angles)
        # Example:
        servo_angle = int((value - 50) / 50 * 180)  # Map 50-100 to 0-180 degrees
        send_command(f"MOVE_SERVO:0:{servo_angle}") 

root = tk.Tk()
slider = tk.Scale(root, from_=0, to=100, orient="horizontal", command=on_slider_change)
slider.pack()
root.mainloop()
