import speech_recognition as sr

# Initialize recognizer
r = sr.Recognizer()

# Load a pre-recorded audio file instead of using the microphone
with sr.AudioFile('path_to_audio_file.wav') as source:
    audio = r.record(source)

# Recognize speech in the audio file
try:
    print("Transcription: " + r.recognize_google(audio))
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))
