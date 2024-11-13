import tkinter as tk
from tkinter import ttk
from datetime import datetime
import requests
import threading
import speech_recognition as sr


# Function to update the clock
def update_time():
    current_time = datetime.now().strftime("%H:%M:%S")
    time_label.config(text=current_time)
    time_label.after(1000, update_time)  # Updates every second
def get_weather():
    api_key = '8c4a0471b913c4daaebb05379f313dab'
    city = 'Providence'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=imperial'
    try:
        response = requests.get(url, timeout=5)# Adding a timeout for safety
        weather_data = response.json()
        if weather_data.get('cod') == 200:
            temp = weather_data['main']['temp']
            description = weather_data['weather'][0]['description'].capitalize()
            return f'{temp}°F, {description}'
        else:
            return 'Weather data not available'
    except Exception:
        return 'Error fetching weather data'
def update_weather():
    def fetch_weather():
        weather_info = get_weather()
        weather_label.config(text=weather_info)
    # Start a new thread to fetch weather data
    weather_thread = threading.Thread(target=fetch_weather)
    weather_thread.daemon = True# Ensure the thread exits when the main program does
    weather_thread.start()

    root.after(60000, update_weather)# Schedule next weather update in 60 seconds

def add_task_with_voice():
    recognizer = sr.Recognizer()
    mic = sr.Microphone(device_index=1)
    with mic as source:
        todo_entry.delete(0, tk.END)  # Clear existing text
        todo_entry.insert(0, "Listening...")  # Show feedback
        # recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjusts to background noise
        recognizer.pause_threshold = 0.8
        try:
            audio = recognizer.listen(source, timeout=5)
            task = recognizer.recognize_google(audio)
            todo_entry.delete(0, tk.END)  # Clear "Listening..." text
            todo_entry.insert(0, task)  # Display recognized text
            todo_listbox.insert(tk.END, task)  # Add to the to-do list
        except sr.UnknownValueError:
            todo_entry.delete(0, tk.END)
            todo_entry.insert(0, "Could not understand audio")
        except sr.RequestError:
            todo_entry.delete(0, tk.END)
            todo_entry.insert(0, "Network error")

# Initialize the main window
root = tk.Tk()
root.title("SPROUT")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")
root.configure(bg="#FFFBF2")  # Set a soft pastel background color

# Style settings
style = ttk.Style()
style.configure("TFrame", background="#FFE4E1", borderwidth=5, relief="groove")
style.configure("TLabel", background="#FFE4E1", font=("Comic Sans MS", 15, "bold"))

# Create a frame with custom colors and rounded corners for the clock
time_frame = ttk.Frame(root, width=screen_width/2-20, height=40,padding=10, style="TFrame")
time_frame.place(x=20, y=20)
time_frame.pack_propagate(False)
# Real-time clock display inside the frame
time_label = ttk.Label(time_frame, text="", style="TLabel")
time_label.pack()
update_time()

# weather
weather_frame = ttk.Frame(root, width=screen_width/2-20, height=40, padding=10, style="TFrame")
weather_frame.place(x=screen_width/2+10, y=20)
weather_frame.pack_propagate(False)
weather_label = tk.Label(weather_frame, font=("Comic Sans MS", 15, "bold"))
weather_label.pack()
update_weather()

# Placeholder for a to-do list frame with similar styling
todo_frame = ttk.Frame(root, width=screen_width/2-20, height=screen_height-60, padding=10, style="TFrame")
todo_frame.place(x=screen_width/2+10, y=100)

# To-Do List Label
todo_label = ttk.Label(todo_frame, text="To-Do List", font=("Comic Sans MS", 14, "bold"))
todo_frame.pack_propagate(False)
todo_label.pack()

todo_entry = tk.Entry(todo_frame, width=25, font=("Comic Sans MS", 10), bg="#FFFBF2")
todo_entry.pack(pady=5)

# Voice-to-text button
voice_button = tk.Button(todo_frame, text="Add with Voice", font=("Comic Sans MS", 10), bg="#FEC8D8", command=add_task_with_voice)
voice_button.pack(pady=5)

# Manual add button
add_button = tk.Button(todo_frame, text="Add", font=("Comic Sans MS", 10), bg="#FEC8D8", command=lambda: todo_listbox.insert(tk.END, todo_entry.get()))
add_button.pack(pady=5)

# To-Do List display
todo_listbox = tk.Listbox(todo_frame, width=int(screen_width/2-20), height=int(screen_height-100), font=("Comic Sans MS", 10), bg="#FFF0F5")
todo_listbox.pack(pady=5)
# Main loop
root.mainloop()
