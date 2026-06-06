# main.py

import time
import platform
from enum import Enum
import threading

target_window = "Code"
current_window = ""

class AppState(Enum):
    FOCUSED = "focused"
    DISTRACTED = "distracted"
    ALERT = "alert"

state = AppState.FOCUSED
total = 1800
start_time = time.time()
paused_time_remaining = None
time_remaining = total
distracted_timer = 0

# --- ALL FUNCTIONS DEFINED FIRST ---

def get_active_window_mac():
    global current_window
    import subprocess
    script = 'tell application "System Events" to get name of first application process whose frontmost is true'
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    current_window = result.stdout.strip()
    return result.stdout.strip()

def get_active_window_windows():
    global current_window
    import pygetwindow as gw
    try:
        current_window = gw.getActiveWindow().title
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
    global state, paused_time_remaining, distracted_timer
    while True:
        current_window = get_active_window()
        print(f"active window: {current_window}")
        if state == AppState.ALERT:
            time.sleep(2)
            continue
        if current_window == target_window:
            if state == AppState.DISTRACTED:
                paused_time_remaining = time_remaining
                distracted_timer = 0
            state = AppState.FOCUSED
        else:
            state = AppState.DISTRACTED
        time.sleep(0.5)

def timer_loop():
    global time_remaining, paused_time_remaining, distracted_timer, state, start_time
    while True:
        if state == AppState.FOCUSED:
            elapsed = time.time() - start_time
            if paused_time_remaining == None:
                time_remaining = total - elapsed
            else:
                time_remaining = paused_time_remaining - elapsed
            print(f"timer: {time_remaining:.0f}s remaining")
            time.sleep(1)
        elif state == AppState.DISTRACTED:
            time.sleep(1)
            distracted_timer += 1
            print(f"distracted for {distracted_timer}s")
            if distracted_timer >= 5: # Change to 300 (5 minutes) for production
                state = AppState.ALERT
        elif state == AppState.ALERT:
            print("ALERT: get back to work")
            time.sleep(5) # Change to 15 seconds for production
            paused_time_remaining = time_remaining
            distracted_timer = 0
            start_time = time.time()
            print("--- switched to focused ---")
            state = AppState.FOCUSED

# --- THEN START THREADS ---

# Without threading, timer_loop and window_monitor_loop would block each other.
# Threading lets both run simultaneously in the background.
t1 = threading.Thread(target=timer_loop, daemon=True)
t2 = threading.Thread(target=window_monitor_loop, daemon=True)
t1.start()
t2.start()

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