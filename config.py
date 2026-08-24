import time

target_window=""
current_window=""

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
total = 1800
start_time = time.time()
paused_time_remaining = None
time_remaining = total
distracted_timer = 0

distraction_time_limit = 300 # Represents 5 minutes

# Search for something in string
def char_is_in(t, input_text):
    for i in range(len(input_text)):
        if t == input_text[i]:
            return True
    return False

def anchor_session_over():
    print("Congrats you finished your anchor in! Here is some feedback:\n")
    print("TBD")