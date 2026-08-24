import base64
import os
from openai import OpenAI
from dotenv import load_dotenv
import config
# In .env the dot just means it's a hidden file on Mac/Linux — files starting with . don't show up in Finder or ls by default. It's a convention for configuration files you don't want cluttering your project view.

load_dotenv()
client = OpenAI(
    # Get an environment variable, return None if it doesn't exist. The optional second argument can specify an alternate default. key, default and the result are str.
    api_key=os.getenv("OPENAI_API_KEY")
)

def image_to_base64(filepath):
    with open(filepath, "rb") as f: # rb as in read bits
        # The f is just like a placeholder variable...
        data = f.read()
    return base64.b64encode(data).decode("utf-8")

SYSTEM_MESSAGE = """You are a focus recovery assistant built for people with ADHD. Your job is to write a short, sharp re-orientation message the moment a user has drifted away from their work. It should be a psychologically-informed message shown to the user in the full-screen alert when they have been off their target window for 5+ minutes. The message should re-orient them to where they left off and motivate them to return to work.
        You understand two core things about the ADHD brain:

        1. **Time blindness:** The brain has no reliable internal clock. Once a distraction becomes "NOW," the original task stops existing. Your message must make the task feel immediate and real again — not abstract or future.
        2. **Switching costs:** Re-engaging after distraction takes real cognitive effort. Your message should lower that friction by doing the memory work for them — tell them exactly where they were so they don't have to reconstruct it.

        You will receive two screenshots and session context: what the user is supposed to be working on, how much time they have left, and which application they should be focused on. The first image shows what the user was doing right before they got distracted. The second image shows what they are currently doing.

        Write exactly 4 sentences. The first sentence restores their working memory — be specific about visible content, not just app names. The second sentence pulls them forward. The third sentence should show an understanding of the situation and remind the user of their goal and urgency of the task. The fourth sentence should demonstrate a successful interpretation of cause of distraction and a breakdown of the use of the distraction app and what specifically they were looking at based on the distracted.png.

        Rules:

        - Never use guilt, shame, or negative framing. Distraction is a neurological event, not a moral failure.
        - Be direct and energizing, not preachy
        - Do not use filler phrases like "It looks like..." or "It seems you were..."
        - Do not summarize both images — use them to write as if you already know what happened
        - Do not mention that you are an AI or that you analyzed their screen
        - Do not ask them to "try harder" or "stay focused" — give them a concrete next action instead"""
        
PROMPT_STYLES = {
    "urgency": "In the fourth sentence, after naming what specifically they were distracted by, close with urgency — make the time remaining feel visceral and immediate.",
    "specificity": "In the fourth sentence, after naming what specifically they were distracted by, close by naming exactly where they left off in their work.",
    "momentum": "In the fourth sentence, after naming what specifically they were distracted by, close by implying they were close to finishing something — make returning feel like the natural next move.",
    "social": "In the fourth sentence, after naming what specifically they were distracted by, close by referencing that others in their session are still focused."
}


def generate_message(style, goal, target_app, time_remaining, priority, task_context):
    last_focus_b64 = image_to_base64("captures/last_focus.png")
    distracted_b64 = image_to_base64("captures/distracted.png")
    prompt_style_instruction = PROMPT_STYLES[style] # Select a style from the PROMPT_STYLES dictionary
    
    user_text = f"""
    The user is working on: {goal}
    Target application: {target_app}
    Time remaining: {time_remaining} minutes
    Priority: {priority}
    Task context: {task_context}
    """
    # We are dropping prompt_style_instruction from the user_text and instead are putting it inside "instruction"
    
    instruction = f"""
    Write the 4-sentence re-orientation message now, following the rules above and using the two provided images and extrapolating a response from the user_text and crafting a message that is understanding of the situation, psychologically informed, re-orients them to where they left off, and motivates them to return to work.
    {prompt_style_instruction}
    """
    
    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": [
            {"type": "text", "text": user_text},
            {"type": "image_url",
             "image_url": {
                 "url": f"data:image/png;base64,{last_focus_b64}",
                 "detail": "high"
             }
            },
            {"type": "image_url",
             "image_url": {
                 "url": f"data:image/png;base64,{distracted_b64}",
                 "detail": "high"
             }
            },
            {"type": "text", "text": instruction}
        ]}
    ]
    response = client.chat.completions.create(model="gpt-5.6-luna", messages=messages)
    return response.choices[0].message.content

if __name__ == "__main__":
    print(generate_message(
        style=config.style,
        goal=config.goal,
        target_app=config.target_window,
        time_remaining=config.time_remaining,
        priority=config.priority,
        task_context=config.task_context
    ))