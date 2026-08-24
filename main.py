# main.py

import time
import platform
from enum import Enum
import threading
import os
import mss
from PIL import Image
import config
from openai import OpenAI
from dotenv import load_dotenv

'''
These are the things the user needs to provide us first and foremost:
Goal — what they are working on
Time goal — how long they want to lock in for
Time remaining — how much time is left in the session
Target application — e.g. VSCode, Google Docs
Priority/urgency level — how important/time-sensitive the task is
Task context — e.g. class assignment, research, independent project, studying, exam prep, meeting prep
'''

'''
Ultimatley users can make something similar to an itinerary, where they can add tasks and anchored sessions into a queue or something,
and if they create a new task and they set it priority high and there is already a priority high task in the queue (if queue not empty),
then it compares the two and asks the user between those two which has higher priority or something.
- Alternatively, while the queue is empty once they add a task they don't a priority,
  but when the queue is NOT empty they are asked to choose is this higher priority then X task or lower priority, and systematically organizes them all into an ordered queue
'''

def get_open_window_names():
    os_system = platform.system()
    if os_system == "Darwin":
        import subprocess
        script = 'tell application "System Events" to get name of every process whose background only is false'
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        return [name.strip() for name in result.stdout.split(",")]
    elif os_system == "Windows":
        import pygetwindow as gw
        return [t for t in gw.getAllTitles() if t.strip()]
    else:
        return []

def prompt_target_window():
    valid_names = get_open_window_names()
    while True:
        entered = input("What application should you be focused on?\n").strip()
        match = next((n for n in valid_names if n.lower() == entered.lower()), None)
        if match:
            return match
        print(f"'{entered}' isn't currently open. Open windows: {', '.join(valid_names)}")

print(config.target_window)
class AppState(Enum):
    FOCUSED = "focused"
    DISTRACTED = "distracted"
    ALERT = "alert"

config.state = AppState.FOCUSED
config.total = 10
config.start_time = time.time()
config.paused_time_remaining = None
config.time_remaining = config.total
config.distracted_timer = 0

os.makedirs("captures", exist_ok=True)

# --- ALL FUNCTIONS DEFINED FIRST ---

def get_active_window_mac():
    import subprocess
    script = 'tell application "System Events" to get name of first application process whose frontmost is true'
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    config.current_window = result.stdout.strip()
    return result.stdout.strip()

def get_active_window_windows():
    import pygetwindow as gw
    try:
        config.current_window = gw.getActiveWindow().title
        return gw.getActiveWindow().title
    except:
        return None

def get_active_window():
    os_system = platform.system()
    if os_system == "Darwin":
        return get_active_window_mac()
    elif os_system == "Windows":
        return get_active_window_windows()
    else:
        return None

def window_monitor_loop():
    # global state, paused_time_remaining, distracted_timer
    while True:
        config.current_window = get_active_window()
        # print(f"active window: {current_window}")
        if config.state == AppState.ALERT:
            time.sleep(0.5)
            continue
        elif config.current_window == config.target_window:
            img = capture_screen()
            img.save("captures/last_focus.png")
            if config.state == AppState.DISTRACTED:
                config.distracted_timer = 0
                config.paused_time_remaining = config.time_remaining
            config.state = AppState.FOCUSED
        else:
            img = capture_screen()
            img.save("captures/distracted.png")
            # Captures what they were working on right before getting distracted — only fires once on transition
            config.state = AppState.DISTRACTED
        time.sleep(0.5)

def timer_loop():
    # global time_remaining, paused_time_remaining, distracted_timer, state, start_time
    while True:
        # Make sure the two lines below work as intended
        if config.state == AppState.FOCUSED:
            elapsed = time.time() - config.start_time
            # if elapsed == config.total and config.distracted_timer < config.distraction_time_limit:
            #     config.anchor_session_over() # CALL THIS NEW FUNCTION FOR WHEN THEY HAVE A SUCCESSFUL LOCKIN SESSION
            #     break
            if config.paused_time_remaining == None:
                config.time_remaining = config.total - elapsed
            else:
                config.time_remaining = config.paused_time_remaining - elapsed
            print(f"timer: {config.time_remaining:.0f}s remaining")
            print(f"current app: {config.current_window}")
            time.sleep(1)
        elif config.state == AppState.DISTRACTED:
            time.sleep(1)
            config.distracted_timer += 1
            print(f"distracted for {config.distracted_timer}s")
            print(f"current app: {config.current_window}")
            if config.distracted_timer >= config.distraction_time_limit: # Change to 300 (5 minutes) for production
                config.state = AppState.ALERT
        elif config.state == AppState.ALERT:
            # Blur the entire screen
            # 15 seconds for AI context bridge & emptying brain animation
            # 15 seconds for task-switching game & filling brain animation
            config.paused_time_remaining = config.time_remaining
            config.distracted_timer = 0
            # Captures what they are currently distracted by when the alert fires
            print("[blurred screen]")
            time.sleep(1)
            print("AI context bridge & brain animation 1")
            from llm import generate_message
            generate_message(config.style, config.goal, config.target_window, config.time_remaining, config.priority, config.task_context)
            time.sleep(5) # Change to 15 seconds for production
            print("Task-switching micro-game")
            time.sleep(5) # Change to 15 seconds for production
            config.start_time = time.time()
            print("--- switched to focused ---")
            config.state = AppState.FOCUSED

# --- CAPTURE SCREEN FUNCTIONALITY ---

# capture_screen() returns a PIL Image object (essentially an in-memory representation of the screenshot
# that you can save to disk, convert to base64 to send to an LLM, and resize, crop, or manipulate w/PIL)
def capture_screen():
    with mss.MSS() as sct:
        screenshot = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        return img

# --- THEN START THREADS ---

# Without threading, timer_loop and window_monitor_loop would block each other.
# Threading lets both run simultaneously in the background.
def start_anchored():
    while True:
        print("Hello! Welcome to Anchored!")
        # Are you a first time user? Yes/No?
        config.goal = input("What are you working on? (e.g. finishing the lit review section)\n")
        config.total = 60 * float(input("How many minutes do you want to anchor in for?\n"))
        while config.total < 1500:
            config.total = 60 * float(input("You need to anchor in for at least 25 minutes.\nHow many minutes do you want to anchor in for?\n"))
        config.target_window = prompt_target_window()
        config.current_window = get_active_window()
        config.priority = input("How urgent is this? (low/medium/high)\n")
        # if config.char_is_in(':', config.total.lower()):
        #     # Interpret as end time relative to current time
        config.task_context = input("What's this for? (e.g. class assignment, research, studying, meeting prep)\n")
        t1 = threading.Thread(target=timer_loop, daemon=True)
        t2 = threading.Thread(target=window_monitor_loop, daemon=True)
        t1.start()
        t2.start()
        # from llm import generate_message
        # generate_message(config.style, config.goal, config.target_window, config.time_remaining, config.priority, config.task_context)

start_anchored()
# t1 = threading.Thread(target=timer_loop, daemon=True)
# t2 = threading.Thread(target=window_monitor_loop, daemon=True)
# t1.start()
# t2.start()

# Keep program alive
while True:
    time.sleep(1)

"""
platform.system
Returns the system/OS name, such as 'Linux', 'Darwin', 'Java', 'Windows'. An empty string is returned if the value cannot be determined.

timer component (threading.Thread)
Provides a way to run multiple threads (smaller units of process) concurrently within a single process. It allows for the creation and management of threads, making it possible to execute tasks in parallel, sharing memory space.

time.time() gives you the current time right now. start_time is the time when the session started.

state machine
The app is a state machine. It always knows what "mode" it's in, and that mode determines what's allowed to happen. In Python, the simplest way is an enum.
"""