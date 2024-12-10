import tkinter as tk
from tkinter import ttk
from datetime import datetime
import requests
import threading
import speech_recognition as sr
import re

import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag, ne_chunk
from nltk.tree import Tree




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
    # mic = sr.Microphone()
    with mic as source:
        todo_entry.delete(0, tk.END)  # Clear existing text
        todo_entry.insert(0, "Listening...")  # Show feedback
        recognizer.pause_threshold = 0.8
        try:
            audio = recognizer.listen(source, timeout=5)
            task = recognizer.recognize_google(audio)
            todo_entry.delete(0, tk.END)  # Clear "Listening..." text
            todo_entry.insert(0, task)  # Display recognized text
            add_task(task)  # Add to the to-do list
        except sr.UnknownValueError:
            todo_entry.delete(0, tk.END)
            todo_entry.insert(0, "Could not understand audio")
        except sr.RequestError:
            todo_entry.delete(0, tk.END)
            todo_entry.insert(0, "Network error")

def listen_for_keyword(keyword):
    recognizer = sr.Recognizer()
    # mic = sr.Microphone(device_index=1)
    mic = sr.Microphone()
    
    if mic:
        print("Microphone initialized.")
    
    with mic as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source)

    print("Listening for keyword...")
    while True:
        with mic as source:
            try:
                # Capture audio
                audio = recognizer.listen(source, timeout=5)
                command = recognizer.recognize_google(audio).lower()
                print(f"You said: {command}")

                # Trigger the task addition function when "calendar" is heard
                if keyword.lower() in command:
                    todo_entry.insert("Keyword detected. Listening for 5 seconds...")
                    print("Keyword detected. Listening for 5 seconds...")   
                    start_time = datetime.now()
                    while (datetime.now() - start_time).seconds < 5:
                        try:
                            audio = recognizer.listen(source, timeout=5)
                            task_command = recognizer.recognize_google(audio).lower()
                            print(f"Task command: {task_command}")
                            add_task(task_command)
                            break
                        except sr.UnknownValueError:
                            print("Sorry, I could not understand the audio.")
                        except sr.RequestError as e:
                            print(f"Error with speech recognition service: {e}")
                        except Exception as ex:
                            print(f"Unexpected error: {ex}")
                    
                    continue  # Skip to the next iteration of the outer while loop
            except sr.UnknownValueError:
                print("Sorry, I could not understand the audio.")
            except sr.RequestError as e:
                print(f"Error with speech recognition service: {e}")
            except Exception as ex:
                print(f"Unexpected error: {ex}")

def add_task(task):
    # Use NLTK to identify entities in the task
    tokens = word_tokenize(task)
    tagged = pos_tag(tokens)
    named_entities = ne_chunk(tagged)
    
    time_keywords = []
    date_keywords = []
    
    for subtree in named_entities:
        if isinstance(subtree, nltk.Tree):
            if subtree.label() == 'TIME':
                time_keywords.append(" ".join([token for token, pos in subtree.leaves()]))
            elif subtree.label() == 'DATE':
                date_keywords.append(" ".join([token for token, pos in subtree.leaves()]))
    
    # Combine all identified keywords
    all_keywords = date_keywords + time_keywords
    for keyword in all_keywords:
        task = task.replace(keyword, '').strip()
    
    # Remove identified keywords and their prepositions from the task
    for token, pos in tagged:
        if pos == 'IN':  # 'IN' is the POS tag for prepositions
            task = task.replace(token, '').strip()
    
    # Format the task label text
    label_text = " ".join(all_keywords) + "           " + task
    
    task_frame = ttk.Frame(todo_frame, width=int(screen_width/2-40), height=40, padding=5, style="TFrame")
    task_frame.pack(pady=5, anchor='w')  # Align to the left
    task_label = ttk.Label(task_frame, text=label_text, style="TLabel")
    task_label.pack(side='left', anchor='w')  # Align to the left
    # Add a checkbox to mark the task as completed
    completed_var = tk.BooleanVar()
    completed_checkbox = ttk.Checkbutton(task_frame, variable=completed_var)
    completed_checkbox.pack(side='left', padx=(30, 0))  # Add space between text and checkbox

def animate_creature_with_images():
    global creature_image_index

    # Update the image displayed
    creature_image_index = (creature_image_index + 1) % len(creature_images)
    canvas.itemconfig(creature, image=creature_images[creature_image_index])

    # Get the current coordinates of the creature (center point)
    x, y = canvas.coords(creature)

    # Reverse direction if the creature hits the canvas bounds
    if x - image_width // 2 < 0 or x + image_width // 2 > canvas.winfo_width():
        animate_creature_with_images.dx *= -1
    if y - image_height // 2 < 0 or y + image_height // 2 > canvas.winfo_height():
        animate_creature_with_images.dy *= -1

    # Move the creature
    canvas.move(creature, animate_creature_with_images.dx, animate_creature_with_images.dy)

    # Schedule the next frame
    root.after(1300, animate_creature_with_images)

root = tk.Tk()
root.title("SPROUT")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")
root.configure(bg="#FFFBF2")  # Set a soft pastel background color

# Placeholder for a to-do list frame with similar styling
todo_frame = ttk.Frame(root, width=screen_width/2-20, height=screen_height-60, padding=10, style="TFrame")
todo_frame.place(x=screen_width/2+10, y=75)

# To-Do List Label
todo_label = ttk.Label(todo_frame, text="To-Do List", font=("Comic Sans MS", 12, "bold"))
todo_frame.pack_propagate(False)
todo_label.pack()

todo_entry = tk.Entry(todo_frame, width=int(screen_width/2-20), font=("Comic Sans MS", 10), bg="#FFFBF2")
todo_entry.pack(pady=5)

# Voice-to-text button
voice_button = tk.Button(todo_frame, text="Add with Voice", font=("Comic Sans MS", 10), bg="#FEC8D8", command=add_task_with_voice)
voice_button.pack(pady=5)

# Manual add button
add_button = tk.Button(todo_frame, text="Add", font=("Comic Sans MS", 10), bg="#FEC8D8", command=lambda: [add_task(todo_entry.get()), todo_entry.delete(0, tk.END)])
add_button.pack(pady=5)


canvas = tk.Canvas(root, width=100, height=100, bg="#FFFBF2", highlightthickness=0)
canvas.place(x=10, y=screen_height - 200)
creature_image_index = 0

# Load and rescale the creature images
creature_images = [
    tk.PhotoImage(file="creature1.png").subsample(2,2),
    tk.PhotoImage(file="creature2.png").subsample(2,2),
    tk.PhotoImage(file="creature3.png").subsample(2,2)
]

image_width = creature_images[0].width()
image_height = creature_images[0].height()

canvas = tk.Canvas(root, width=image_width, height=image_height, bg="#FFFBF2", highlightthickness=0)
canvas.place(x=10, y=screen_height - image_height)

# Add the first frame of the creature animation
creature = canvas.create_image(image_width // 2, image_height // 2, image=creature_images[creature_image_index])

# Animate the creature with images


# Initialize movement
animate_creature_with_images.dx = 5  # Adjust speed if needed
animate_creature_with_images.dy = 5

# Start the animation
animate_creature_with_images()

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

keyword_thread = threading.Thread(target=listen_for_keyword, args=("calendar",), daemon=True)
keyword_thread.start()
root.mainloop()
