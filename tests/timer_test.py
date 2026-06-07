import time
from enum import Enum
import threading

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
print("--- switched to focused ---")
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
                state = AppState.ALERT # You need global state
        elif state == AppState.ALERT:
            print("ALERT: get back to work")
            time.sleep(5) # Change to 15 seconds for production
            paused_time_remaining = time_remaining
            distracted_timer = 0
            start_time = time.time()
            print("--- switched to focused ---")
            state = AppState.FOCUSED

# Without threading, if you just called timer_loop() directly, it would run the while True loop forever and the rest of your code below it would never execute. Threading lets timer_loop run in the background while your main program keeps going and does other things.
t1 = threading.Thread(target=timer_loop, daemon=True)
# target=timer_loop tells it which function to run.
# daemon=True means it dies when the main program exits.
t1.start()

time.sleep(10)
state = AppState.DISTRACTED # Simulating getting distracted after 10 seconds of focus
paused_time_remaining = time_remaining
print("--- switched to distracted ---")

time.sleep(30) # Keep program alive long enough to see alert fire and resume