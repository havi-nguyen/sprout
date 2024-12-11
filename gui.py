import tkinter as tk
from tkinter import ttk
from datetime import datetime
import requests
import threading
import speech_recognition as sr
import re

import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk import Tree
from nltk.corpus import treebank_chunk
from nltk.chunk import ne_chunk

animation_running = True
global task_frames
task_frames = []

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

# def add_task_with_voice():
#     recognizer = sr.Recognizer()
#     mic = sr.Microphone(device_index=1)
#     # mic = sr.Microphone()
#     with mic as source:
#         todo_entry.delete(0, tk.END)  # Clear existing text
#         todo_entry.insert(0, "Listening...")  # Show feedback
#         recognizer.pause_threshold = 0.8
#         try:
#             audio = recognizer.listen(source, timeout=5)
#             task = recognizer.recognize_google(audio)
#             todo_entry.delete(0, tk.END)  # Clear "Listening..." text
#             todo_entry.insert(0, task)  # Display recognized text
#             add_task(task)  # Add to the to-do list
#         except sr.UnknownValueError:
#             todo_entry.delete(0, tk.END)
#             todo_entry.insert(0, "Could not understand audio")
#         except sr.RequestError:
#             todo_entry.delete(0, tk.END)
#             todo_entry.insert(0, "Network error")

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
                    # todo_entry.insert("Keyword detected. Listening for 5 seconds...")
                    todo_entry.insert(0, "Listening for 7 seconds...")
                    print("Keyword detected. Listening for 7 seconds...")   
                    start_time = datetime.now()
                    while (datetime.now() - start_time).seconds < 10:
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
                    todo_entry.delete(0, tk.END)
                    continue  # Skip to the next iteration of the outer while loop
            except sr.UnknownValueError:
                print("Sorry, I could not understand the audio.")
            except sr.RequestError as e:
                print(f"Error with speech recognition service: {e}")
            except Exception as ex:
                print(f"Unexpected error: {ex}")
#create an object of task: include date, time, and task
class TaskEntry:
    def __init__(self, time, date, task,am_pm):
        self.time = time
        self.date = date
        self.task = task
        self.am_pm = am_pm
def add_task(task):
    # Use NLTK to identify entities in the task
    tokens = word_tokenize(task)
    tagged = pos_tag(tokens)
    named_entities = ne_chunk(tagged)
    print(tagged)
    print(named_entities,type(named_entities),type(named_entities[-1]))
    new_task = TaskEntry("", "", "", "")
    #time regex
    # time = re.search(r'\d{1,2}:\d{2}(?:am|pm)', task,re.IGNORECASE)
    # if time:
    #     task = task.replace(time.group(), '').strip()
    #     new_task.time = time.group()
    # date=re.search(r'\b(?:\d{1,2}[-/th|st|nd|rd\s.]*)?(January|February|March|April|May|June|July|August|September|October|November|December)?\d{1,4}\b', task,re.IGNORECASE)
    # if date:
    #     task = task.replace(date.group(), '').strip()
    #     new_task.date = date.group()
    # weekday = re.search(r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b', task,re.IGNORECASE)
    # print(weekday)
    # if weekday:
    #     task = task.replace(weekday.group(), '').strip()
    #     new_task.date = weekday.group()
    # print('Task:', new_task.task, 'Time:', str(new_task.time), 'Date:', str(new_task.date))
    time_keywords = []
    date_keywords = []
    am_keywords=[]
    remove=[]
    #recognize time and date
    for subtree in named_entities:
        if hasattr(subtree, 'label'):
             print('yeedeeeee')
        elif isinstance(subtree, Tree) and subtree.label() == 'DATE':
            date_keywords.append(" ".join(token for token, pos in subtree.leaves()))
        elif isinstance(subtree, Tree) and subtree.label() == 'TIME':
            time_keywords.append(" ".join(token for token, pos in subtree.leaves()))
    
    date_pattern = re.compile(r'\b(?:\d{1,2}[/-]?\d{1,2}[/-]?\d{2,4}|'
                          r'(?:January|February|March|April|May|June|July|August|September|October|November|December)|'
                          r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday))\b', re.IGNORECASE)
    time_pattern = re.compile(r'\b\d{1,2}', re.IGNORECASE)
    am_pm= re.compile(r'\b(?:a.m|p.m)\b', re.IGNORECASE)
    # Extract date and time keywords from the task
    for match in date_pattern.finditer(task):
        date_keywords.append(match.group())
    for match in time_pattern.finditer(task):
        time_keywords.append(match.group())
    for match in am_pm.finditer(task):
        am_keywords.append(match.group())
    print('Date keywords:', date_keywords)
    print('Time keywords:', time_keywords)
    print('AM keywords:', am_keywords)
    task = task.replace(':', '').strip() 
    # Combine all identified keywords
    all_keywords = date_keywords + time_keywords + am_keywords
    for keyword in all_keywords:
        task = task.replace(keyword, '').strip()
    task = task.replace('.', '').strip() 
    # new_task.task = task
    # print('Task:', new_task.task, 'Time:', str(new_task.time), 'Date:', str(new_task.date))
    # Remove identified keywords and their prepositions from the task
    for token, pos in tagged:
        if pos == 'IN':  # 'IN' is the POS tag for prepositions
            task = task.replace(token, '').strip()
    new_task = TaskEntry("", "", "", "")
    new_task.task = task
    new_task.time = time_keywords if len(time_keywords) > 0 else ""
    new_task.date = date_keywords if len(date_keywords) > 0 else ""
    new_task.am_pm = am_keywords[0] if len(am_keywords) > 0 else ""
    
    # Format the task label text
    # label_text = f"{new_task.time}"+ str(' ') + f"{new_task.weekday}"+ str(' ') +f"{new_task.date})"+ str('         ') + f"{new_task.task}"
    if len(time_keywords)==0:
        label_text=" ".join(date_keywords) + "    " + task
    else:
        label_text = " ".join(date_keywords) + " " + time_keywords[0] + ":" + time_keywords[1] + " " + " ".join(am_keywords) + "    " + task


    
    global task_frame  # Make task_frame accessible outside of this function
    task_frame = ttk.Frame(todo_frame, width=int(screen_width/2-40), height=40, padding=5, style="TFrame")
    task_frame.pack(pady=5, anchor='w')  # Align to the left
    task_label = ttk.Label(task_frame, text=label_text, style="TLabel")
    task_label.pack(side='left', anchor='w')  # Align to the left
    # Add a checkbox to mark the task as completed
    completed_var = tk.BooleanVar()
    completed_checkbox = ttk.Checkbutton(task_frame, variable=completed_var)
    completed_checkbox.var = completed_var
    completed_checkbox.pack(side='left', padx=(70, 0))  # Add space between text and checkbox

    completed_checkbox.completed_triggered = False

    # Add the new task_frame to a list for future reference
    task_frames.append((task_frame, completed_checkbox))
    
#check if the task is completed
def check_completed():
  for task_frame, checkbox in task_frames:
        if isinstance(checkbox, ttk.Checkbutton):
            # Get the associated variable from the Checkbutton
            checkbox_state = checkbox.var.get()  # Access the BooleanVar value
            if checkbox_state and not checkbox.completed_triggered:  # If checked and not triggered yet
                checkbox.completed_triggered = True  # Mark as triggered
                play_completed_animation()  # Start the special animation

        root.after(1000, check_completed)  # Continue checking

def animate_creature_with_images():
    global creature_image_index

    if not animation_running:
        return 
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

def resume_main_animation():
    global animation_running
    animation_running = True
    animate_creature_with_images()  # Restart the main animation

root = tk.Tk()
root.title("SPROUT")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")
root.configure(bg="#e9efe7")  # Set a soft pastel background color

# Placeholder for a to-do list frame with similar styling
todo_frame = ttk.Frame(root, width=screen_width/2-20, height=screen_height-60, padding=10, style="TFrame")
todo_frame.place(x=screen_width/2+10, y=75)

# To-Do List Label
todo_label = ttk.Label(todo_frame, text="To-Do List", font=("Verdana", 15, "bold"))
todo_frame.pack_propagate(False)
todo_label.pack()

todo_entry = tk.Entry(todo_frame, width=int(screen_width/2-20), font=("Verdana", 15), bg="#FFFBF2")
todo_entry.pack(pady=5)

# Voice-to-text button
# voice_button = tk.Button(todo_frame, text="Add with Voice", font=("Verdana", 10), bg="#FEC8D8", command=add_task_with_voice)
# voice_button.pack(pady=5)

# # # Manual add button
# add_button = tk.Button(todo_frame, text="Add", font=("Verdana", 10), bg="#FEC8D8", command=lambda: [add_task(todo_entry.get()), todo_entry.delete(0, tk.END)])
# add_button.pack(pady=5)

canvas = tk.Canvas(root, width=100, height=100, bg="#FFFBF2", highlightthickness=0)
canvas.place(x=10, y=screen_height - 200)
creature_image_index = 0

# Load and rescale the creature images
creature_images = [
    tk.PhotoImage(file="radish_files/creature1.png").subsample(2,2),
    tk.PhotoImage(file="radish_files/creature2.png").subsample(2,2),
    tk.PhotoImage(file="radish_files/creature3.png").subsample(2,2)
]

image_width = creature_images[0].width()
image_height = creature_images[0].height()

canvas = tk.Canvas(root, width=image_width, height=image_height, bg="#FFFBF2", highlightthickness=0)
canvas.place(x=10, y=screen_height - image_height)

# Add the first frame of the creature animation
creature = canvas.create_image(image_width // 2, image_height // 2, image=creature_images[creature_image_index])

# Animate the creature with images
# Load and rescale the alternate images for completed task animation
completed_task_images = [
    tk.PhotoImage(file="radish_files/happy1.png").subsample(2, 2),
    tk.PhotoImage(file="radish_files/happy2.png").subsample(2, 2),
    tk.PhotoImage(file="radish_files/happy3.png").subsample(2, 2)
]

# Function to play the alternate animation
def play_completed_animation():
    loops_remaining = 2  # Number of loops
    current_image_index = 0

    def update_image():
        nonlocal loops_remaining, current_image_index
        if loops_remaining > 0:
            canvas.itemconfig(creature, image=completed_task_images[current_image_index])
            current_image_index = (current_image_index + 1) % len(completed_task_images)
            if current_image_index == 0:  # Loop completed
                loops_remaining -= 1
            root.after(500, update_image)  # Change image every 500 ms
        else:
            resume_main_animation()  # Resume the main animation after completion

    global animation_running
    animation_running = False  # Pause main animation
    update_image()


# Initialize movement
animate_creature_with_images.dx = 5  # Adjust speed if needed
animate_creature_with_images.dy = 5

# Start the animation
animate_creature_with_images()

# Style settings
style = ttk.Style()
style.configure("TFrame", background="#e9efe7", borderwidth=5, relief="groove")
style.configure("TLabel", background="#FFE4E1", font=("Verdana", 15, "bold"))

# Create a frame with custom colors and rounded corners for the clock
time_frame = ttk.Frame(root, width=screen_width/2-20, height=40,padding=10, style="TFrame")
time_frame.place(x=20, y=20)
time_frame.pack_propagate(False)
# Real-time clock display inside the frame
time_label = ttk.Label(time_frame, text="", style="TLabel")
time_label.pack()
update_time()


def display_store():
    global animation_running

    # Stop the animation
    animation_running = False

    # Remove all widgets from the root window
    for widget in root.winfo_children():
        widget.destroy()

    # Add a frame for the store layout
    store_frame = ttk.Frame(root, width=screen_width, height=screen_height, style="TFrame")
    store_frame.pack(fill="both", expand=True)

    # Add a title for the store
    store_title = ttk.Label(store_frame, text="Store", font=("Verdana", 30, "bold"), anchor="center", style="TLabel")
    store_title.pack(pady=20)

    # Add a frame for items layout
    items_frame = ttk.Frame(store_frame)
    items_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Sample items with images and prices
    items = [
        {"image": "radish_files/creature1.png", "price": "$10.99"},
        {"image": "radish_files/creature2.png", "price": "$15.49"},
        {"image": "radish_files/creature3.png", "price": "$20.00"},
    ]

    # Display items in a grid
    for i, item in enumerate(items):
        # Load and display the image
        img = tk.PhotoImage(file=item["image"]).subsample(2, 2)  # Adjust scaling as needed
        image_label = tk.Label(items_frame, image=img, bg="#e9efe7")
        image_label.image = img  # Keep a reference to avoid garbage collection
        image_label.grid(row=i // 3 * 2, column=i % 3, padx=20, pady=10)

        # Display the price below the image
        price_label = ttk.Label(items_frame, text=item["price"], font=("Verdana", 12, "bold"))
        price_label.grid(row=i // 3 * 2 + 1, column=i % 3, padx=20, pady=5)
 
# Create a frame for the buttons
button_frame = ttk.Frame(root, width=screen_width/2-20, height=40, padding=10, style="TFrame")
button_frame.place(x=20, y=80)  # Place it under the clock

# Configure the grid layout for spacing
button_frame.columnconfigure(0, weight=1)  # First column for the Store button
button_frame.columnconfigure(1, weight=1)  # Second column (empty) for spacing
button_frame.columnconfigure(2, weight=1)  # Third column for the Items button

# Add the "Store" button
store_button = ttk.Button(button_frame, text="Store", command=display_store, style="TLabel")
store_button.grid(row=0, column=0, padx=5, sticky="e")  # Place the Store button

# Add the "Items" button
items_button = ttk.Button(button_frame, text="Items", command=lambda: print("Items button clicked"), style="TLabel")
items_button.grid(row=0, column=2, padx=5, sticky="w")  # Place the Items button

# weather
weather_frame = ttk.Frame(root, width=screen_width/2-20, height=40, padding=10, style="TFrame")
weather_frame.place(x=screen_width/2+10, y=20)
weather_frame.pack_propagate(False)
weather_label = tk.Label(weather_frame, font=("Verdana", 15, "bold"))
weather_label.pack()
update_weather()


radish_hungry = 100
# Update health bar and label in the same row as "Store" and "Items"
def decrease_health():
    global radish_hungry

    if radish_hungry > 0:
        radish_hungry -= 5  # Decrease health by 5
        health_bar['value'] = radish_hungry
        health_label.config(text=f"Health: {radish_hungry}%")
    else:
        health_label.config(text="Radish Health: 0% (Radish is unhealthy!)")
        return  # Stop decreasing if health reaches 0

    root.after(2000, decrease_health)  # Repeat every 2 seconds


# Radish health bar and label in the button_frame
health_label = ttk.Label(button_frame, text=f"Health: {radish_hungry}%", font=("Verdana", 12, "bold"))
health_label.grid(row=0, column=3, padx=10, sticky="w")

health_bar = ttk.Progressbar(button_frame, orient="horizontal", length=200, mode="determinate")
health_bar['value'] = radish_hungry
health_bar.grid(row=0, column=4, padx=5, sticky="w")

# Call function to decrease health periodically
decrease_health()

check_completed()
keyword_thread = threading.Thread(target=listen_for_keyword, args=("calendar",), daemon=True)
keyword_thread.start()
# Start a new thread to keep the check_completed function running in the background
# check_completed_thread = threading.Thread(target=check_completed, daemon=True)
# check_completed_thread.start()


root.mainloop()
