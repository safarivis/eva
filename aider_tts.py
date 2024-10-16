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
        # Run Aider with the user query
        # This command might vary based on your specific Aider setup
        response = subprocess.check_output(["python", "-m", "aider", user_input], text=True)

        # Print and speak the response
        print(response.strip())  # Print the response to console
        speak(response.strip())   # Speak the response
    except subprocess.CalledProcessError as e:
        print(f"Error while calling Aider: {e.output}")
        speak("There was an error trying to get a response from Aider.")

print("Exited Aider interaction.")
