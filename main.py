# main.py

from enum import Enum
import threading
import os
import config
import json
import time

from tracker import get_open_window_names, get_active_window, window_monitor_loop, timer_loop

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

def prompt_target_window():
    valid_names = get_open_window_names()
    while True:
        entered = input("What application should you be focused on?\n").strip()
        match = next((n for n in valid_names if n.lower() == entered.lower()), None)
        if match:
            return match
        print(f"'{entered}' isn't currently open. Open windows: {', '.join(valid_names)}")

print(config.target_window)

#  The line below is a one-time setup call that runs at module load, before start_anchored() and before any thread starts, so captures/ always exists before capture_screen() is ever called.
os.makedirs("captures", exist_ok=True)

# Without threading, timer_loop and window_monitor_loop would block each other.
# Threading lets both run simultaneously in the background.
def start_anchored():
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
    
    # SESSION BEGINS HERE
    config.state = config.AppState.FOCUSED
    config.start_time = time.time()
    config.paused_time_remaining = None
    config.time_remaining = config.total
    config.distracted_timer = 0
    config.break_bool = False
    
    t1 = threading.Thread(target=timer_loop, daemon=True)
    t2 = threading.Thread(target=window_monitor_loop, daemon=True)
    t1.start()
    t2.start()
    
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

# When do we start the latency timer?
# When time.time() = start_time + distracted_timer + time_remaining

'''
alert_start = time.time()  # when alert fires
# ... user sees message ...
alert_end = time.time()  # when they return to target window
return_latency = alert_end - alert_start
'''