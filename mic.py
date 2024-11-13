import speech_recognition as sr

# List all available microphones and their indexes
for index, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"Microphone {index}: {name}")