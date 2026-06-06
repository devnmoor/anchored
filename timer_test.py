import time
from enum import Enum
import threading

class AppState(Enum):
    FOCUSED = "focused"
    DISTRACTED = "distracted"

state = AppState.FOCUSED
total = 1800
start_time = time.time()
paused_time_remaining = None
time_remaining = total

def timer_loop():
    while True:
        if state == AppState.FOCUSED:
            elapsed = time.time() - start_time
            if paused_time_remaining == None:
                time_remaining = total - elapsed
            else:
                time_remaining = paused_time_remaining - elapsed
            print(time_remaining)
            time.sleep(1)

# Without threading, if you just called timer_loop() directly, it would run the while True loop forever and the rest of your code below it would never execute.Threading lets timer_loop run in the background while your main program keeps going and does other things.
t1 = threading.Thread(target = timer_loop, daemon = True)
# target=timer_loop tells it which function to run.
# daemon=True means it dies when the main program exits.
t1.start()


time.sleep(10)
state = AppState.DISTRACTED # Simulating getting distracted after 10 seconds of focus
paused_time_remaining = time_remaining
print("switched to distracted")

time.sleep(5)
state = AppState.FOCUSED
start_time = time.time()
print("switched back to focused")

time.sleep(10)