**`llm_test.py` TODO**
1. Delete the bad `messages` list at the top of the file
2. Move the system message into a `SYSTEM_MESSAGE` constant string
3. Write `generate_message()` — inside it:
   - Build `user_text` f-string with goal, target_app, time_remaining, priority, task_context, prompt_style_instruction
   - Build `messages` list with system message + user message (text + 2 images)
   - Call `client.chat.completions.create(model="gpt-4o", messages=messages)`
   - Extract and return the text from the response object
4. Test it by calling `generate_message()` with hardcoded values and the two saved screenshots from `captures/`
5. Confirm the output is a real 2-sentence message
6. Add logging — save prompt style used + return latency to a JSON file each time it's called
