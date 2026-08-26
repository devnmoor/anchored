import mss
from PIL import Image

# capture_screen() returns a PIL Image object (essentially an in-memory representation of the screenshot
# that you can save to disk, convert to base64 to send to an LLM, and resize, crop, or manipulate w/PIL)
def capture_screen():
    with mss.MSS() as sct:
        screenshot = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        return img