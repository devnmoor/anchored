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

def timer_loop():
    time_remaining = total
    while True:
        if state == AppState.FOCUSED:
            elapsed = time.time() - start_time
            if paused_time_remaining == None:
                time_remaining = total - elapsed
            else:
                time_remaining = paused_time_remaining - elapsed
            print(time_remaining)
            time.sleep(1)
        elif state == AppState.DISTRACTED:
            paused_time_remaining = time_remaining # Move to where we switch to DISTRACTED, not a bug, just messy
timer_loop()

# Without threading, if you just called timer_loop() directly, it would run the while True loop forever and the rest of your code below it would never execute.Threading lets timer_loop run in the background while your main program keeps going and does other things.
t1 = threading.Thread(target = timer_loop, daemon = True)
# target=timer_loop tells it which function to run.
# daemon=True means it dies when the main program exits.
t1.start()


time.sleep(10)

time.sleep