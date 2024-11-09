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

# Initialize the main window
root = tk.Tk()
root.title("Cute Real-Time Clock with To-Do List")
root.geometry("700x500")
root.configure(bg="#FFFBF2")  # Set a soft pastel background color

# Style settings
style = ttk.Style()
style.configure("TFrame", background="#FFE4E1", borderwidth=5, relief="groove")
style.configure("TLabel", background="#FFE4E1", font=("Comic Sans MS", 30, "bold"))

# Create a frame with custom colors and rounded corners for the clock
time_frame = ttk.Frame(root, width=300, height=60,padding=10, style="TFrame")
time_frame.place(x=20, y=20)
time_frame.pack_propagate(False)
# Real-time clock display inside the frame
time_label = ttk.Label(time_frame, text="", style="TLabel")
time_label.pack()
update_time()

# weather
weather_frame = ttk.Frame(root, width=350, height=60, padding=10, style="TFrame")
weather_frame.place(x=350, y=20)
weather_label = tk.Label(weather_frame, font=('Helvetica', 20), bg='#2c3e50', fg='#ecf0f1')
weather_label.pack(pady=5)
update_weather()

# Placeholder for a to-do list frame with similar styling
todo_frame = ttk.Frame(root, width=350, height=460, padding=10, style="TFrame")
todo_frame.place(x=350, y=100)

# To-Do List Label
todo_label = ttk.Label(todo_frame, text="To-Do List", font=("Comic Sans MS", 14, "bold"))
todo_frame.pack_propagate(False)
todo_label.pack()

# Entry for new tasks
todo_entry = tk.Entry(todo_frame, width=250, font=("Comic Sans MS", 10),bg="#FFFBF2")
todo_entry.pack(pady=5)

# Buttons to add tasks with a pastel button background color
add_button = tk.Button(todo_frame, text="Add", font=("Comic Sans MS", 10), bg="#FEC8D8", command=lambda: todo_listbox.insert(tk.END, todo_entry.get()))
add_button.pack(pady=5)

# To-Do List display
todo_listbox = tk.Listbox(todo_frame, width=300, height=400, font=("Comic Sans MS", 10), bg="#FFF0F5")
todo_listbox.pack(pady=5)

# Main loop
root.mainloop()
