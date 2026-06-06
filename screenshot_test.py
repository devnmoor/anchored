from mss import MSS
from PIL import Image
from enum import Enum

class AppState(Enum):
    FOCUSED = "focused"
    DISTRACTED = "distracted"
    ALERT = "alert"
    
state = AppState.DISTRACTED

def capture_screen():
    with MSS() as sct:
        screenshot = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        return img

def save_sct(img):
    if state == AppState.DISTRACTED:
        img.save("distracted.png")
    elif state == AppState.FOCUSED:
        img.save("last_focus.png")
img = capture_screen()
save_sct(img)