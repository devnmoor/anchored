import config
import time
from llm import generate_message
import json

# --- FIRE ALERT ---
def fire_alert():
    config.alert_start_time = time.time()
    # Blur the entire screen
    # 15 seconds for AI context bridge & emptying brain animation
    # 15 seconds for task-switching game & filling brain animation
    config.paused_time_remaining = config.time_remaining
    config.distracted_timer = 0
    # Captures what they are currently distracted by when the alert fires
    print("[blurred screen]")
    time.sleep(1)
    print("AI context bridge & brain animation 1")
    message = generate_message(config.style, config.goal, config.target_window,
                               config.time_remaining, config.priority, config.task_context)
    print(message + "\n")  # replace with UI display later
    time.sleep(config.ai_bridge_duration)
    
    # BREAK HANDLING
    temp = input("Would you like to continue with the anchor session (1) or take a 5-minute break (2)?\n")
    config.break_bool = False if temp == "1" or temp == "(1)" else True
    if config.break_bool == True:
        config.state = config.AppState.BREAK
        print("5-minute break starting now...")
        time.sleep(5) # 5 minutes
    
    # HANDLE LATER
    # print("Task-switching micro-game")
    # time.sleep(5) # Change to 15 seconds for production
    config.start_time = time.time()
    print("--- switched to focused ---")
    config.state = config.AppState.FOCUSED
    
    # LOGGING
    data_to_log = {
                    "timestamp": f"{config.alert_start_time}", # when the alert fired
                    "latency": f"{config.latency}",
                    "style": f"{config.style}",
                    "messages": f"{message}",
                    "time-remaining": f"{config.time_remaining}", # time remaining in session when alert fired
                    "goal": f"{config.goal}",
                    "task-context": f"{config.task_context}",
                    "break-bool": f"{config.break_bool}"
                }
    with open("log.json", "w") as file:
        json.dump(data_to_log, file, indent=4)