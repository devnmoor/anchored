import config
import platform
import time
from screenshot import capture_screen
from alerts import fire_alert

# --- ALL OS-LEVEL FUNCTIONS ---
# MacOS
def get_active_window_mac():
    import subprocess
    script = 'tell application "System Events" to get name of first application process whose frontmost is true'
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    config.current_window = result.stdout.strip()
    return result.stdout.strip()

# Windows
def get_active_window_windows():
    import pygetwindow as gw
    try:
        config.current_window = gw.getActiveWindow().title
        return gw.getActiveWindow().title
    except:
        return None

# Get active window (GENERAL)
def get_active_window():
    os_system = platform.system()
    if os_system == "Darwin":
        return get_active_window_mac()
    elif os_system == "Windows":
        return get_active_window_windows()
    else:
        return None

# See which windows are open
def get_open_window_names():
    os_system = platform.system()
    if os_system == "Darwin":
        import subprocess
        script = 'tell application "System Events" to get name of every process whose background only is false'
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        return [name.strip() for name in result.stdout.split(",")]
    elif os_system == "Windows":
        import pygetwindow as gw
        return [t for t in gw.getAllTitles() if t.strip()]
    else:
        return []


# --- FOCUS/DISTRACTION TRACKING FUNCTIONS ---
def window_monitor_loop():
    # global state, paused_time_remaining, distracted_timer
    while True:
        config.current_window = get_active_window()
        # print(f"active window: {current_window}")
        if config.state == config.AppState.ALERT:
            time.sleep(0.5)
            continue
        
        # POTENTIAL FIX (TEST...)
        elif config.current_window == config.target_window:
            if config.state == config.AppState.DISTRACTED:  # only on the transition back
                img = capture_screen()
                img.save("captures/last_focus.png")
                config.distracted_timer = 0
                config.paused_time_remaining = config.time_remaining
            config.state = config.AppState.FOCUSED
        else:
            if config.state != config.AppState.DISTRACTED:  # only on the transition into distraction
                img = capture_screen()
                img.save("captures/distracted.png")
            config.state = config.AppState.DISTRACTED

        # elif config.current_window == config.target_window: # If this is a return to focus
        #     config.alert_end_time = time.time()
        #     img = capture_screen()
        #     img.save("captures/last_focus.png")
        #     if config.state == config.AppState.DISTRACTED:
        #         config.distracted_timer = 0
        #         config.paused_time_remaining = config.time_remaining
        #     config.state = config.AppState.FOCUSED
        # else:
        #     img = capture_screen()
        #     img.save("captures/distracted.png")
        #     # Captures what they were working on right before getting distracted — only fires once on transition
        #     config.state = config.AppState.DISTRACTED
        
        time.sleep(0.5)
        
        
# --- TIMER LOGIC ---
def update_timer():
    # FOCUSED
    if config.state == config.AppState.FOCUSED:
        elapsed = time.time() - config.start_time
        # if elapsed == config.total and config.distracted_timer < config.distraction_time_limit:
        #     config.anchor_session_over() # CALL THIS NEW FUNCTION FOR WHEN THEY HAVE A SUCCESSFUL LOCKIN SESSION
        #     break
        if config.paused_time_remaining is None: # If the user is not distracted
            config.time_remaining = config.total - elapsed
        else:
            # If they get distracted we subtract how long they are distracted for from however much time they have left in their anchor session:
            config.time_remaining = config.paused_time_remaining - elapsed
        print(f"timer: {config.time_remaining:.0f}s remaining")
        # print(f"current app: {config.current_window}")
        # print(f"paused time remaining: {config.paused_time_remaining}")
        time.sleep(1)
        
    # DISTRACTED
    elif config.state == config.AppState.DISTRACTED:
        time.sleep(1)
        config.distracted_timer += 1
        print(f"distracted for {config.distracted_timer}s")
        # print(f"current app: {config.current_window}")
        # print(f"paused time remaining: {config.paused_time_remaining}")
        if config.distracted_timer >= config.distraction_time_limit:
            config.state = config.AppState.ALERT
            
# --- TIMER LOOP (GENERAL) ---
def timer_loop():
    while True:
        if config.state == config.AppState.ALERT:
            fire_alert()
        else:
            update_timer()