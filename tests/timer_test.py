import time
from enum import Enum
import threading
import config

class AppState(Enum):
    FOCUSED = "focused"
    DISTRACTED = "distracted"
    ALERT = "alert"
    
config.state = AppState.FOCUSED
config.total = 1800
config.start_time = time.time()
config.paused_time_remaining = None
config.time_remaining = config.total
config.distracted_timer = 0
print("--- switched to focused ---")

def timer_loop():
    # global time_remaining, paused_time_remaining, distracted_timer, state, start_time
    while True:
        if config.state == AppState.FOCUSED:
            elapsed = time.time() - config.start_time
            if config.paused_time_remaining == None:
                config.time_remaining = config.total - elapsed
            else:
                config.time_remaining = config.paused_time_remaining - elapsed
            print(f"timer: {config.time_remaining:.0f}s remaining")
            time.sleep(1)
        elif config.state == AppState.DISTRACTED:
            time.sleep(1)
            config.distracted_timer += 1
            print(f"distracted for {config.distracted_timer}s")
            if config.distracted_timer >= 5: # Change to 300 (5 minutes) for production
                config.state = AppState.ALERT # You need global state
        elif config.state == AppState.ALERT:
            print("ALERT: get back to work")
            time.sleep(5) # Change to 15 seconds for production
            config.paused_time_remaining = config.time_remaining
            config.distracted_timer = 0
            config.start_time = time.time()
            print("--- switched to focused ---")
            config.state = AppState.FOCUSED

# Without threading, if you just called timer_loop() directly, it would run the while True loop forever and the rest of your code below it would never execute. Threading lets timer_loop run in the background while your main program keeps going and does other things.
t1 = threading.Thread(target=timer_loop, daemon=True)
# target=timer_loop tells it which function to run.
# daemon=True means it dies when the main program exits.
t1.start()

time.sleep(10)
config.state = AppState.DISTRACTED # Simulating getting distracted after 10 seconds of focus
config.paused_time_remaining = config.time_remaining
print("--- switched to distracted ---")

time.sleep(30) # Keep program alive long enough to see alert fire and resume