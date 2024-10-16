import speech_recognition as sr

# Initialize recognizer
r = sr.Recognizer()

# Option 2: Skip the microphone input and proceed without audio
audio = None  # Skip the microphone and set audio to None as a placeholder

# Continue with the rest of your code
try:
    if audio:
        print("Transcription: " + r.recognize_google(audio))
    else:
        print("No audio input, skipping recognition.")
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print(f"Could not request results from Google Speech Recognition service; {e}")
