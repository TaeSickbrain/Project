import serial

ser = serial.Serial('COM7', 9600)  # Replace 'COM3' with your Arduino's port

def send_command(command):
    """
    Send a command to the Arduino.
    """
    ser.write((command + "\n").encode())
    time.sleep(0.1)  # Allow time for Arduino to process
