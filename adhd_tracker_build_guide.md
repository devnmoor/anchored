# ADHD Focus Tracker — Build Guide

## What You're Building

A desktop app that:
1. Lets you set a task and start a timer
- Enter task, how long you need to spend
2. Monitors which window you're in
- Enter the main application
- Expects that you stay in that application in full screen
3. Alerts you if you've been away from your work window for 5+ minutes
- When window inactive for more than 5 minutes, show full window alert/notification that says return to your work
- It includes AI generated message that tells them something like "You only have 30 minutes until you need to send out emails, don't get distracted and complete this task."
- Given two options: "Take a 5 minute break" or "Continue task"
    - Taking a 5 minute break prevents you from taking a break the next time you are inactive for 5 minutes (but it resets after that next task)
You can also lock your screen so you can't move around to other windows at all.
4. Captures the screen at the moment of distraction
- To get them back on track, it captures screen at the moment of distraction and also from right before they went away from the window
- Every time they go away from the window, whether or not it was less than 5 minutes or over 5 minutes resulting in an alert, the app screenshots their last work, sometimes that screenshot is used and sometimes not if they went back to the window before 5 minutes.
- So when they are distracted for over 5 minutes, the window tells them that right now they are "...." and 5 minutes ago they were "....", so they should continue the latter, ... (This message should be written very carefully and should be written in a way that poeople with ADHD, suddenly get motivated to go back to work, based on actual ADHD research and manipulation of the mind to change tasks...)
5. Sends it to an LLM to generate a 2-sentence "here's what you were doing" re-orientation summary
...
---

## Tech Stack

| Component | Tool | Why |
|---|---|---|
| Window tracking | `pygetwindow` + `psutil` | Simple, cross-platform |
| Screen capture | `mss` | Fast, lightweight |
| LLM summarization | OpenAI or Anthropic API (vision) | Send screenshot → get summary |
| Alerts | `plyer` (notifications) + `playsound` | OS-native notifications |
| UI | `tkinter` (built into Python) | No install needed, good enough for MVP |
| Eye tracking (Phase 2) | `mediapipe` | Webcam-based gaze detection |

---

## Setup

### Prerequisites
- Python 3.10+
- An OpenAI API key (get one at platform.openai.com) — GPT-4o has vision built in
- Git

### Install dependencies
```bash
pip install pygetwindow psutil mss plyer playsound openai pillow
```

On Mac, `pygetwindow` has limited support — use `pyobjc` instead:
```bash
pip install pyobjc-framework-Quartz
```

---

## Phase 1: Window Activity Tracker (Week 1–2)

**Goal:** Detect when the user leaves their target window for 5 minutes and fire an alert.

### Step 1 — Get the active window title

```python
import pygetwindow as gw
import time

def get_active_window():
    try:
        return gw.getActiveWindow().title
    except:
        return None

# Test it
while True:
    print(get_active_window())
    time.sleep(2)
```

Run this, click around different apps, and confirm it's printing the right window titles.

### Step 2 — Track time away from target window

```python
import pygetwindow as gw
import time

def monitor(target_window, threshold_seconds=300):
    time_away = 0
    check_interval = 10  # check every 10 seconds

    while True:
        active = get_active_window()
        if active and target_window.lower() in active.lower():
            time_away = 0  # reset counter when back on task
        else:
            time_away += check_interval
            print(f"Away for {time_away}s")

        if time_away >= threshold_seconds:
            alert()
            time_away = 0  # reset after alerting

        time.sleep(check_interval)
```

### Step 3 — Fire an alert

```python
from plyer import notification

def alert():
    notification.notify(
        title="Get back to work",
        message="You've been away from your task for 5 minutes.",
        timeout=10
    )
```

**Milestone:** You now have a working distraction detector. Test it by setting your target window to "VSCode" or a browser tab, then switching away for 5 minutes.

---

## Phase 2: Screen Capture + LLM Re-orientation (Week 3–4)

**Goal:** When the alert fires, capture the screen and generate a summary of what the user was last doing.

### Step 4 — Capture the screen

```python
import mss
from PIL import Image
import io
import base64

def capture_screen():
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])  # primary monitor
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        return img

def image_to_base64(img):
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
```

### Step 5 — Send to LLM and get summary

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key-here")

def summarize_screen(img, task_description):
    b64 = image_to_base64(img)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"The user was working on: '{task_description}'. Based on this screenshot, write exactly 2 sentences summarizing what they were doing and where they left off. Be specific — mention visible content, not just app names."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{b64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=100
    )
    return response.choices[0].message.content
```

### Step 6 — Wire it together

Modify your `alert()` function:

```python
def alert(task_description):
    img = capture_screen()
    summary = summarize_screen(img, task_description)

    notification.notify(
        title="Get back to work",
        message=summary,
        timeout=15
    )
```

**Milestone:** You now have the core product. When you drift away, it captures your screen, summarizes where you were, and tells you in the notification.

---

## Phase 3: Basic UI (Week 5–6)

**Goal:** A simple window where the user types their task, sets the timer, and starts monitoring.

```python
import tkinter as tk
from tkinter import messagebox
import threading

class FocusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Focus Tracker")
        self.monitoring = False

        tk.Label(root, text="What are you working on?").pack(pady=5)
        self.task_entry = tk.Entry(root, width=50)
        self.task_entry.pack(pady=5)

        tk.Label(root, text="Target window name (e.g. VSCode, Chrome):").pack(pady=5)
        self.window_entry = tk.Entry(root, width=50)
        self.window_entry.pack(pady=5)

        self.start_btn = tk.Button(root, text="Start", command=self.start)
        self.start_btn.pack(pady=10)

        self.status_label = tk.Label(root, text="Not monitoring")
        self.status_label.pack()

    def start(self):
        task = self.task_entry.get()
        window = self.window_entry.get()
        if not task or not window:
            messagebox.showwarning("Missing info", "Please fill in both fields.")
            return
        self.monitoring = True
        self.status_label.config(text=f"Monitoring: {window}")
        thread = threading.Thread(target=monitor, args=(window, task, 300), daemon=True)
        thread.start()

root = tk.Tk()
app = FocusApp(root)
root.mainloop()
```

---

## Phase 4: Eye Tracking (Week 7–8, optional but impressive)

**Goal:** Use webcam to detect when the user looks away from the screen as a secondary distraction signal.

```bash
pip install mediapipe opencv-python
```

```python
import cv2
import mediapipe as mp

def start_eye_tracking():
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            print("No face detected — user may have looked away")
            # increment away counter here

        # Use landmarks 468-477 for iris tracking if you want gaze direction
```

This is the hardest part — don't let it block Phase 1–3. Add it last.

---

## Demo Video Checklist (End of Summer)

Record a 90-second screen recording showing:
- [ ] User types task + target window, hits Start
- [ ] User switches to Twitter/YouTube for a few minutes
- [ ] Alert fires with the LLM summary ("You were reading about X on page Y")
- [ ] User clicks back to work
- [ ] (If done) Eye tracking detecting gaze away from screen

Keep it under 2 minutes. No narration needed — let it speak for itself.

---

## Resume Bullet Points

Once built, describe it like this:

> Built a multimodal focus recovery system that monitors window activity and webcam gaze, detects distraction events, and uses GPT-4o vision to generate context-aware re-orientation summaries — restoring task context in under 3 seconds.

Quantify whatever you can measure: latency, accuracy of distraction detection, etc.

---

## Weekly Checklist

- [ ] **Week 1:** Window tracker running, alerts firing correctly
- [ ] **Week 2:** Tested on 3+ apps, edge cases handled (window not found, multiple monitors)
- [ ] **Week 3:** Screen capture working, LLM summarization returning good output
- [ ] **Week 4:** Full alert → capture → summarize → notify loop working end to end
- [ ] **Week 5:** Basic tkinter UI complete
- [ ] **Week 6:** Polish, error handling, test with real work sessions
- [ ] **Week 7:** Eye tracking integrated (optional)
- [ ] **Week 8:** Demo video recorded, GitHub README written, pushed publicly
