import speech_recognition as sr

def start_voice_control(sensitivity):
    """
    Start listening for voice commands.
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say a command...")
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio).lower()
        print(f"Command: {command}")
        # Process the command (e.g., "move to handle", "close gripper")
        # ...
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
