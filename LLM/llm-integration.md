### What an LLM API is
You are basically sending a **request** over the internet **to a server** (e.g., OpenAI, Anthropic, etc.) that **runs the model**. You send text in, you get text back. It's just an HTTP request, like how a website loads, except you're sending a prompt and receiving a response.

### Basic structure of every API call
1. The **authentication** - your API key proves you're allowed to use it (and charges your account)
2. The **request** - your prompt, which model to use, and any settings like max response length
3. The **response** — the model's output, returned as a Python object you can read

**Multimodal (text + images)**
Newer models like GPT-4o and Claude can accept images alongside text. Instead of just sending a string as `content`, you send a list that contains both text and image data. The image has to be encoded as base64 — a way of representing binary file data (like a PNG) as a plain text string that can travel over the internet.


Order matters because LLMs read prompts sequentially and give more weight to context that's set up early.Order matters because LLMs read prompts sequentially and give more weight to context that's set up early. Generally:
- Set the context first (who the user is, what they're doing)
- Then provide the evidence (images)
- Then give the instruction (what to generate)

1. Context: "The user is working on X and has Y minutes remaining"
2. Evidence: last_focus image, then distracted image
3. Instruction: "Write a message that does A, B, C in style Z"
