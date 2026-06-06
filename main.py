# main.py

import time
import platform
from enum import Enum

class AppState(Enum):
    FOCUSED = "focused"
    DISTRACTED = "distracted"
    ALERT = "alert"
    BREAK = "break"

# This singular variable holds the current state
state = AppState.FOCUSED
total = 1800 # Should be user input
start_time = time.time()
paused_time_remaining = None

def timer_loop():
    while True:
        if state == AppState.FOCUSED:
            # count down timer
            elapsed = time.time() - start_time
            time_remaining = total - elapsed
            print(time_remaining)
            time.sleep(2)
        # elif state == AppState.DISTRACTED:
        #     # count down distraction_timer
        # elif state == AppState.ALERT:
        #     # count down alert_timer
        # elif state == AppState.BREAK:
        #     # count down break_timer
        # else:
        #     # do nothing

def get_active_window():
    os_system = platform.system()
    if os_system == "Darwin":
        return get_active_window_mac()
    elif os_system == "Windows":
        return get_active_window_windows()
    else:
        return None

def get_active_window_mac():
    import subprocess
    script = 'tell application "System Events" to get name of first application process whose frontmost is true'
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    return result.stdout.strip()
    
def get_active_window_windows():
    import pygetwindow as gw
    try:
        return gw.getActiveWindow().title
    except:
        return None
    

while True:
    print(get_active_window())
    time.sleep(1)
    
"""
platform.system
Returns the system/OS name, such as 'Linux', 'Darwin', 'Java', 'Windows'. An empty string is returned if the value cannot be determined.

timer component (threading.Thread)
Provides a way to run multiple threads (smaller units of process) concurrently within a single process. It allows for the creation adn management of threads, making it possible to execute tasks in parallel, sharing memory space. 
time.time() gives you the current time right now. start_time is the time when the session started.

state machine
The app is a state machine. It always knows what "mode" it's in, and that mode determines what's allowed to happen. In Python, the simplest way is an enum:
"""