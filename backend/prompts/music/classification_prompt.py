def classification_prompt(current_input: str, previous_prompt: str) -> str:
    # If there is no previous prompt, use the fresh start logic
    if not previous_prompt.strip():
        return f"""
        You are a strict classifier. Your only job is to determine if the user is asking to create, generate, or describe music or audio.

        Rules:
        * If the input asks for music (example: "make a lofi beat", "give me a jazz song"), respond MUSIC.
        * If the input is conversational or unrelated (example: "hello", "what time is it"), respond NOT_MUSIC.

        Respond ONLY with "MUSIC" or "NOT_MUSIC". Do not include any other words.

        Current Input: "{current_input}"
        """
    
    # If there is a previous prompt, use the modification logic
    else:
        return f"""
        You are a strict classifier. The user is currently in an active music generation session.

        Rules:
        * NEW REQUEST: If the current input asks for a completely new song (example: "now make a rock song instead"), respond MUSIC.
        * MODIFICATION: If the current input asks to change or add to the previous music (example: "add heavy drums", "make it faster", "more energetic"), respond MUSIC.
        * UNRELATED: If the current input is completely unrelated to music or the previous prompt (example: "thanks", "how are you"), respond NOT_MUSIC.

        Respond ONLY with "MUSIC" or "NOT_MUSIC". Do not include any other words.

        Previous Prompt: "{previous_prompt}"
        Current Input: "{current_input}"
        """