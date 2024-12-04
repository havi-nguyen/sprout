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

    todo_entry = tk.Entry(todo_frame, width=25, font=("Comic Sans MS", 10), bg="#FFFBF2")
    todo_entry.pack(pady=5)

    add_button = tk.Button(todo_frame, text="Add", font=("Comic Sans MS", 10), bg="#FEC8D8", command=lambda: todo_listbox.insert(tk.END, todo_entry.get()))
    add_button.pack(pady=5)

    todo_listbox = tk.Listbox(todo_frame, width=int(screen_width / 2 - 20), height=int(screen_height - 100), font=("Comic Sans MS", 10), bg="#FFF0F5")
    todo_listbox.pack(pady=5)

    checkbox_var = tk.BooleanVar()
    checkbox = tk.Checkbutton(todo_frame, text="Task Completed", variable=checkbox_var, font=("Comic Sans MS", 10), bg="#FFFBF2")
    checkbox.pack(pady=5)

    # Calendar Button
    calendar_button = tk.Button(root, text="Calendar", font=("Comic Sans MS", 12, "bold"), bg="#FADADD", command=open_calendar)
    calendar_button.place(x=20, y=100)

    # Enable touch response for all widgets
    for widget in [time_frame, weather_frame, todo_frame, todo_entry, add_button, todo_listbox, checkbox, calendar_button]:
        enable_touch_response(widget)

    # Bind swipe events to the root window
    root.bind("<ButtonPress-1>", swipe_start)
    root.bind("<ButtonRelease-1>", swipe_end)

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

# Enable touch response on Raspberry Pi
def enable_touch_response(widget):
    widget.bind("<Button-1>", lambda e: widget.focus_set())

# Load the home screen on startup
load_home_screen()

root.mainloop()
