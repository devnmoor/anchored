import time
from enum import Enum

# --- APP STATE ---
class AppState(Enum):
    FOCUSED = "focused"
    DISTRACTED = "distracted"
    ALERT = "alert"
    BREAK = "break"

state = None # Set by main.py at startup

# --- SESSION CONTEXT (set once by start_anchored(), never guessed) ---
goal = None
target_window = None
priority = None
task_context = None
total = None # Session length in seconds, from user input

# --- RUNTIME STATE (derived/updated continuously during a session) ---
current_window="" # Setting it to "" is harmless because it gets replaced almost instantly at runtime
start_time = None # User-defined
paused_time_remaining = None # The time they have left to be distracted before alert fires
time_remaining = None # This is total time remaining in the anchored session
distracted_timer = 0
break_bool = False

# --- ALERT TELEMETRY (per-alert, reset each time an alert fires) ---
alert_start_time = None
alert_end_time = None

# --- STYLE (RL-controlled later..., static default for now) ---
style = "urgency"

# --- CONSTANTS ---
distraction_time_limit = 5    # 5 minutes of distraction before an alert fires (Note: value may be changed for testing!)
ai_bridge_duration = 15         # 15 seconds of AI context bridge & brain animation stays up <-- NOT TO SURE ABOUT THIS


def anchor_session_over():
    print("Congrats you finished your anchor in! Here is some feedback:\n")
    print("TBD")
    
    
    
    
    
    
    
    
    

'''
# Use urgency as the defaul prompt style
style="urgency" # Handle the actual RL in this because this is based on the user's patterns and the model learns from their habits and how succesful they benefit from using anchored.
# Run experiments using W&B to simulate the user's improvement in terms of their concentration and focus, it should be measured over the span _____ time.
# How would this work and what is the most efficient way to collect this user data and user reinforcement learning?
# Anchored shoudl be useful to the user from the start and not require a lot of training and testing with the user before hand, we will always have new users
# There should be a starting DEFAULT STYLE and stuff set for new users and it should adapt as the user uses Anchored more.
# Does this mean that we will need more styles for the prompt, or what's the best way to really personalize and improve for each user that will make this project quite successful and impactful?
goal="" # ✅

### NEED TO DO
# We also want the LLM can guage the sense of urgency or whatever by asking follow ups if needed after receiving a response from user.
# For example, if user says the goal is finishign the lit review section, the LLM could ask a follow up, saying is this for a class? or is this an assignment? does this have a set due date? are you stressed about completing it? how far are you with this section?

state=""
total=1800
start_time = time.time()
paused_time_remaining = None
time_remaining = total
distracted_timer = 0
priority = "high"
task_context = ""
break_bool = False

alert_start_time=0
alert_end_time=0
latency=alert_end_time-alert_start_time


distraction_time_limit = 5 # Represents 5 minutes
ai_bridge_duration = 15 # Seconds the AI context bridge & brain animation stays up

# Search for something in string
def char_is_in(t, input_text):
    for i in range(len(input_text)):
        if t == input_text[i]:
            return True
    return False

def anchor_session_over():
    print("Congrats you finished your anchor in! Here is some feedback:\n")
    print("TBD")
'''