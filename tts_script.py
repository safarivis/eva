import pyttsx3
import subprocess

# Initialize the TTS engine
engine = pyttsx3.init()

# Function to speak the text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Main loop to interact with Aider
while True:
    # Ask the user for input
    user_input = input("Ask Aider: ")
    
    if user_input.lower() == 'exit':
        break

    # Call Aider and capture the response
    try:
        # Adjust the command as needed to fit how you run Aider
        response = subprocess.check_output(["python", "-m", "aider", user_input], text=True)

        # Print and speak the response
        print(response)  # Print the response to console
        speak(response)   # Speak the response
    except Exception as e:
        print(f"Error: {e}")
        speak("There was an error trying to get a response from Aider.")

print("Exited Aider interaction.")
