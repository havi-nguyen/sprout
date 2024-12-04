import tkinter as tk
from tkinter import ttk
from datetime import datetime
import requests
import threading

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
        response = requests.get(url, timeout=5)  # Adding a timeout for safety
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
    weather_thread.daemon = True  # Ensure the thread exits when the main program does
    weather_thread.start()

    root.after(60000, update_weather)  # Schedule next weather update in 60 seconds

# Function to open the calendar page and replace the current screen
def open_calendar():
    # Clear all existing widgets on the screen
    for widget in root.winfo_children():
        widget.destroy()

    # Add calendar-specific content
    tk.Label(root, text="Calendar Page", font=("Comic Sans MS", 30, "bold")).pack(pady=50)
    tk.Button(root, text="Back to Home", font=("Comic Sans MS", 15), bg="#FADADD", command=load_home).pack(pady=20)

# Function to load the home screen
def load_home():
    # Clear all existing widgets on the screen
    for widget in root.winfo_children():
        widget.destroy()

    # Reload the home screen widgets
    load_home_screen()

# Function to handle swipe gestures
def swipe_start(event):
    global swipe_start_x
    swipe_start_x = event.x

def swipe_end(event):
    global swipe_start_x
    swipe_end_x = event.x
    if swipe_end_x - swipe_start_x > 100:  # Swipe right threshold
        open_calendar()

# Function to load all widgets for the home screen
def load_home_screen():
    # Clock
    global time_label
    time_frame = ttk.Frame(root, width=screen_width / 2 - 20, height=40, padding=10, style="TFrame")
    time_frame.place(x=20, y=20)
    time_frame.pack_propagate(False)
    time_label = ttk.Label(time_frame, text="", style="TLabel")
    time_label.pack()
    update_time()

    # Weather
    global weather_label
    weather_frame = ttk.Frame(root, width=screen_width / 2 - 20, height=40, padding=10, style="TFrame")
    weather_frame.place(x=screen_width / 2 + 10, y=20)
    weather_frame.pack_propagate(False)
    weather_label = tk.Label(weather_frame, font=("Comic Sans MS", 15, "bold"))
    weather_label.pack()
    update_weather()

    # To-Do List
    todo_frame = ttk.Frame(root, width=screen_width / 2 - 20, height=screen_height - 60, padding=10, style="TFrame")
    todo_frame.place(x=screen_width / 2 + 10, y=100)
    todo_frame.pack_propagate(False)

    global todo_entry, todo_listbox
    todo_label = ttk.Label(todo_frame, text="To-Do List", font=("Comic Sans MS", 14, "bold"))
    todo_label.pack()

    todo_entry = tk.Entry(todo_frame, width=25, font=("Comic Sans MS", 10), bg
