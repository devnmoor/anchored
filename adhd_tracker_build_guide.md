# ADHD Focus Tracker — Build Guide

## What You're Building

A desktop app for people with ADHD that enforces focus, detects distraction, and uses AI to snap the user back on task — fast.

### Core Features

**1. Task + Timer Setup**
- User enters: what they're working on, how long they need to spend on it
- App uses the time remaining as context for all alert messages ("you only have 30 minutes left")

**2. Window Monitoring**
- User specifies the target application (e.g. VSCode, Google Docs)
- App expects that application to stay in the foreground, full screen
- Continuously tracks whether the target window is active

**3. Continuous Screenshot Buffer**
- Every time the user leaves the target window — even briefly — the app silently captures a screenshot of what they were last doing
- This screenshot is stored in a rolling buffer: "last work state" and "5 minutes ago work state"
- Most screenshots are never shown to the user; they're only surfaced if a distraction alert fires

**4. Distraction Alert (5+ minutes away)**
When the user has been away from their target window for more than 5 minutes, the app takes over with a full-screen modal alert. The alert includes:

- An AI-generated re-orientation message that shows two states side by side:
  - *Right now:* "You are currently watching a YouTube video about basketball"
  - *5 minutes ago:* "You were editing slide 4 of your presentation, writing about Q3 revenue"
  - A motivational closer grounded in ADHD psychology (see Messaging Guidelines below)

- Two action buttons:
  - **"Take a 5-minute break"** — grants one guilt-free break; this option is disabled for the remainder of the current task session after it's used once, resetting only when a new task is started
  - **"Continue task"** — dismisses the alert and returns focus to the target window

**5. Optional Focus Lock**
- User can enable a hard lock mode that prevents switching away from the target window entirely
- When active, any attempt to switch windows is immediately blocked or reversed

### Messaging System (ADHD-Informed + Instrumented)

The AI-generated alert message is the most important feature — and the most technically interesting if built right. The goal is not just to generate a message, but to learn over time which kinds of messages actually work for each user.

#### Step 1: Define the metric

The metric you care about is **return latency** — the number of seconds between the alert appearing and the user clicking "Continue task" and staying on the target window. Lower = better. Every alert that fires should log this.

```python
# When alert fires
alert_start_time = time.time()

# When user clicks "Continue task"
return_latency = time.time() - alert_start_time
log_session(prompt_style=current_style, return_latency=return_latency)
```

#### Step 2: Define prompt styles

Rather than using one fixed prompt, define 3–4 distinct styles grounded in ADHD research. Each style emphasizes a different psychological lever:

| Style | What it does | Example |
|---|---|---|
| `urgency` | Ties message to time remaining | "You have 22 minutes left. Don't lose them." |
| `specificity` | Names exactly where they left off | "You were on slide 4, mid-sentence about revenue." |
| `momentum` | Frames return as the satisfying move | "You were almost done with that section." |
| `social` | References competitive session if active | "Your friend hasn't gone off-window once." |

#### Step 3: A/B test across sessions

Rotate through prompt styles and log which produces the lowest return latency. After 20–30 sessions you'll have real data.

```python
import random

PROMPT_STYLES = ["urgency", "specificity", "momentum", "social"]

def pick_prompt_style(user_history):
    if len(user_history) < 12:
        # Not enough data yet — rotate evenly
        return PROMPT_STYLES[len(user_history) % len(PROMPT_STYLES)]
    else:
        # Enough data — weight toward the style with lowest avg return latency
        avg_latency = {
            style: sum(r["latency"] for r in user_history if r["style"] == style) /
                   max(1, sum(1 for r in user_history if r["style"] == style))
            for style in PROMPT_STYLES
        }
        return min(avg_latency, key=avg_latency.get)
```

#### Step 4: Build the prompt dynamically

```python
def build_prompt(style, task, time_remaining, current_screen_desc, last_work_desc):
    base = f"The user is working on: '{task}'. They have {time_remaining} minutes left."
    context = f"Right now: {current_screen_desc}. Five minutes ago: {last_work_desc}."

    if style == "urgency":
        instruction = "Write 2 sentences. Lead with the time remaining as a concrete number. Make it feel urgent but not panicked."
    elif style == "specificity":
        instruction = "Write 2 sentences. Be extremely specific about what they were doing — mention visible content, not just app names."
    elif style == "momentum":
        instruction = "Write 2 sentences. Frame returning to work as the satisfying next move. Imply they were close to finishing something."
    elif style == "social":
        instruction = "Write 2 sentences. Mention that others in their session are still focused. Make returning feel like the obvious choice."

    return f"{base} {context} {instruction} Do not use guilt. Be direct and energizing."
```

#### Step 5: Log everything and report findings

Every session, log: prompt style used, generated message, return latency, whether the user took a break or continued, and how long they stayed on task after returning.

At the end of the summer, even 30–40 sessions of your own usage gives you something to write up:

> *"Urgency framing reduced average return latency by 34% compared to momentum framing for distraction events over 7 minutes. Specificity framing performed best for shorter distraction events (5–7 min)."*

That one sentence in your README or in an interview is the difference between "I called an API" and "I built an instrumented system, ran experiments, and measured outcomes."

---

## Additional Features

**Reward System**
- Users earn points for completing focus sessions without going off-window
- Points accumulate into a high score the user tries to beat over time
- Progress tracking surfaces improvement over days and weeks — a key motivator for ADHD users who respond well to visible momentum

**Competitive Lock-In Sessions**
- Two users can join a shared session and set the same time goal
- At the end, both see a side-by-side breakdown of who was more "locked in" based on:
  - Active typing, clicking, and scrolling
  - Active editing (file saves, code changes, etc.)
  - Number of times off-window and total off-window duration
- The social accountability layer is deliberate — ADHD research consistently shows that body doubling (working alongside someone else) significantly improves focus. This is a digital version of that.

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