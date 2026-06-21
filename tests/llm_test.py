def image_to_base64(filepath):
    with open(filepath, "rb") as f: # rb as in read bits
        # The f is just like a placeholder variable...
        data = f.read()
    return base64.b64encode(data).decode("utf-8")


"""
The LLM receives the following information:
We generally expect that the user keeps the target window open in full screen, now there is that 5-minute distraction countdown, because let's say that you are supposed to stay targeted on VSCode for example, but then don't know how to implement something like a library, you can still search things up on google, it's just that you can't do so for more than 5 minutes at a time.
- gets information from what user entered for that anchor session
    - more generally what they are working on and how long they need to spend on it
    - i.e., focus application, goal, time goal (how long they want to lock in for), if this is urgent and priority work, context about the task (e.g., for a class, for research, independent project, studying, exam, meeting, etc.)
    - User specifies the target application (e.g. VSCode, Google Docs)
    - App expects that application to stay in the foreground, full screen
    - Continuously tracks whether the target window is active
- gets the last_focus.png and the distracted.png
    - last_focus.png represents their screen right before they get distracted
        [- analyze of their screen activity is an enhancement that we can try and implement later, but it could be a lot of work and we can't guarentee it being flawless]
        - Look at the applications open and any main window
        - Gather as much text and context from the image as possible
"""

"""
image_to_base64(filepath) function opens the file at that path in binary mode with the "rb", which means "read bytes"
f.read() reads the entire file as raw bytes (just a long sequence of numbers representing the image data)
base64.b64encode(data) converts those bytes into a base64 encoded sequence (just a way to represent any binary data, like images, audio, or files as plain text using only 64 safe characters [A-Z, a-z, 0-9, +,/])
.decode("utf-8") converts that into a regular Python string
"""
