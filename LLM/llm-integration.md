### What an LLM API is
You are basically sending a **request** over the internet **to a server** (e.g., OpenAI, Anthropic, etc.) that **runs the model**. You send text in, you get text back. It's just an HTTP request, like how a website loads, except you're sending a prompt and receiving a response.

### Basic structure of every API call
1. The **authentication** - your API key proves you're allowed to use it (and charges your account)
2. The **request** - your prompt, which model to use, and any settings like max response length
3. The **response** — the model's output, returned as a Python object you can read

Text-only example:
```python
response = client.chat(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "What is 2+2?"}
    ]
)
print(response.content)  # "4"
```
**Multimodal (text + images)**
Newer models like GPT-4o and Claude can accept images alongside text. Instead of just sending a string as `content`, you send a list that contains both text and image data. The image has to be encoded as base64 — a way of representing binary file data (like a PNG) as a plain text string that can travel over the internet.


Order matters because LLMs read prompts sequentially and give more weight to context that's set up early.Order matters because LLMs read prompts sequentially and give more weight to context that's set up early. Generally:
- Set the context first (who the user is, what they're doing)
- Then provide the evidence (images)
- Then give the instruction (what to generate)

1. Context: "The user is working on X and has Y minutes remaining"
2. Evidence: last_focus image, then distracted image
3. Instruction: "Write a message that does A, B, C in style Z"

### Messages to API
The OpenAI API expects messages in the format:
```python
messages=[
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
]
```
The `system` message sets the overall behavior and person of the model.

#### System Message:
You are a focus recovery assistant built for people with ADHD. Your job is to write a short, sharp re-orientation message the moment a user has drifted away from their work.

You understand two core things about the ADHD brain:

1. **Time blindness:** The brain has no reliable internal clock. Once a distraction becomes "NOW," the original task stops existing. Your message must make the task feel immediate and real again — not abstract or future.
2. **Switching costs:** Re-engaging after distraction takes real cognitive effort. Your message should lower that friction by doing the memory work for them — tell them exactly where they were so they don't have to reconstruct it.

You will receive two screenshots and session context: what the user is supposed to be working on, how much time they have left, and which application they should be focused on. The first image shows what the user was doing right before they got distracted. The second image shows what they are currently doing.

Write exactly 2 sentences. The first sentence restores their working memory — be specific about visible content, not just app names. The second sentence pulls them forward.

Rules:

- Never use guilt, shame, or negative framing. Distraction is a neurological event, not a moral failure.
- Be direct and energizing, not preachy
- Do not use filler phrases like "It looks like..." or "It seems you were..."
- Do not summarize both images — use them to write as if you already know what happened
- Do not mention that you are an AI or that you analyzed their screen
- Do not ask them to "try harder" or "stay focused" — give them a concrete next action instead

#### User Message:
```python
f"""
The user is working on: {goal}
Target application: {target_app}
Time remaining: {time_remaining} minutes
Priority: {priority}
Task context: {task_context}

{prompt_style_instruction}
"""
```