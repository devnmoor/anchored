# main.py

import time
import pygetwindow as gw
import platform

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

"""