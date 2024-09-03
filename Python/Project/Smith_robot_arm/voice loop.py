import serial
import time
import speech_recognition as sr

def main():
    try:
        # Initialize serial connection to Arduino
        arduino = serial.Serial('COM7', 9600)  # Replace 'COM7' with your port
        time.sleep(2)  # Wait for Arduino to reset

        # Initialize the speech recognizer
        recognizer = sr.Recognizer()

        def listen_for_command():
            with sr.Microphone() as source:
                print("Listening for command...")
                audio = recognizer.listen(source)
                try:
                    command = recognizer.recognize_google(audio)
                    print(f"Recognized command: {command}")
                    return command.lower()
                except sr.UnknownValueError:
                    print("Could not understand the command")
                except sr.RequestError:
                    print("Could not request results; check your network connection")
            return ""

        def process_command(command):
            if "turn on" in command:  # New command to move two servos
                command_str1 = '0,90\n'  # Set servo 0 to 90 degrees
                command_str2 = '1,180\n'  # Set servo 1 to 180 degrees
                command_str3 = '2,180\n'  # Set servo 2 to 180 degrees
                arduino.write(command_str1.encode())
                arduino.write(command_str2.encode())
                arduino.write(command_str3.encode())
                print(f"Sent: {command_str1} and {command_str2} and {command_str3}")
            elif "open" in command:
                command_str = '5,0\n'  # Set servo 5 to 45 degrees
                arduino.write(command_str.encode())
                print(f"Sent: {command_str}")
            elif "close" in command:
                command_str = '5,180\n'  # Set servo 5 to 135 degrees
                arduino.write(command_str.encode())
                print(f"Sent: {command_str}")
            elif "reset" in command:  # New command to move two servos
                command_str1 = '0,90\n'  # Set servo 0 to 90 degrees
                command_str2 = '1,90\n'  # Set servo 1 to 90 degrees
                command_str3 = '2,45\n'  # Set servo 2 to 45 degrees
                arduino.write(command_str1.encode())
                arduino.write(command_str2.encode())
                arduino.write(command_str3.encode())
                print(f"Sent: {command_str1} and {command_str2} and {command_str3}")
            elif "dam" in command:  # New command to move two servos
                command_str1 = '0,180\n'  # Set servo 0 to 180 degrees
                command_str2 = '1,150\n'  # Set servo 1 to 150 degrees
                command_str3 = '2,90\n'   # Set servo 2 to 90 degrees
                arduino.write(command_str1.encode())
                arduino.write(command_str2.encode())
                arduino.write(command_str3.encode())
                print(f"Sent: {command_str1} and {command_str2} and {command_str3}")
            else:
                print("Command not recognized")

        while True:
            command = listen_for_command()
            if command:
                process_command(command)

    except serial.SerialException as e:
        print(f"Error with serial connection: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'arduino' in locals() and arduino.is_open:
            arduino.close()
            print("Serial connection closed.")

if __name__ == "__main__":
    main()
