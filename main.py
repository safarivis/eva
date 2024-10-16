import os
import sys
from dotenv import load_dotenv
from datetime import datetime
import random
import speech_recognition as sr
import pyttsx3

def main():
    # Load environment variables from the .env file
    load_dotenv()

    # Initialize the text-to-speech engine
    engine = pyttsx3.init()

    # Announce that the assistant is ready
    speak(engine, "Hello! The assistant is now running. How can I assist you today?")

    # Start listening for voice commands
    listen_for_voice_commands(engine)

def speak(engine, text):
    """Function to speak out the assistant's response."""
    engine.say(text)
    engine.runAndWait()

def listen_for_voice_commands(engine):
    """Function to listen to voice commands using the microphone."""
    recognizer = sr.Recognizer()

    while True:
        try:
            with sr.Microphone() as source:
                print("Listening for a command...")

                # Adjust the recognizer sensitivity to ambient noise
                recognizer.adjust_for_ambient_noise(source)

                # Listen for the user's input
                audio = recognizer.listen(source)

                # Recognize the voice input and convert it to text
                command = recognizer.recognize_google(audio)
                command = command.lower()
                print(f"You said: {command}")

                # Handle the recognized command
                handle_prompt(engine, command)

        except sr.UnknownValueError:
            speak(engine, "Sorry, I did not understand that.")
        except sr.RequestError as e:
            speak(engine, "Sorry, I am having trouble connecting to the speech recognition service.")

def handle_prompt(engine, prompt):
    """Handle the voice command and respond accordingly."""
    if "hello" in prompt:
        response = "Hello! How can I assist you today?"
        print(response)
        speak(engine, response)
    elif "what time is it" in prompt:
        current_time = datetime.now().strftime("%H:%M:%S")
        response = f"The current time is {current_time}."
        print(response)
        speak(engine, response)
    elif "random number" in prompt:
        random_number = random.randint(1, 100)
        response = f"Here is a random number: {random_number}"
        print(response)
        speak(engine, response)
    elif "exit" in prompt or "quit" in prompt:
        response = "Goodbye!"
        print(response)
        speak(engine, response)
        sys.exit()  # Exit the assistant
    else:
        response = f"Sorry, I don't know how to respond to '{prompt}'."
        print(response)
        speak(engine, response)

if __name__ == "__main__":
    main()
