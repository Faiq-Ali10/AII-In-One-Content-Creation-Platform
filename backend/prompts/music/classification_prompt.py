def classification_prompt(input: str, previous_prompt: str) -> str:
    return f"""
    You are a classifier. Respond only with MUSIC or NOT_MUSIC.

    Behavior rules:

    1. If previous_prompt is empty:
    - Classify current_input normally as MUSIC or NOT_MUSIC.
    - If current_input is empty → respond NOT_MUSIC.

    2. If previous_prompt is NOT empty:
    - If current_input clearly requests NEW MUSIC (e.g. "now make a jazz song", "make a rock track instead", "new beat", "let's do something different", "another one"), classify as MUSIC.
    - If current_input appears to MODIFY the previous music request (e.g. "add drums", "make it faster", "add vocals", "make it more energetic"), classify as MUSIC.
    - If current_input is unrelated to music or not requesting music, respond NOT_MUSIC.

    Examples:

    (previous="", input="make a beat") → MUSIC
    (previous="", input="what's up") → NOT_MUSIC
    (previous="chill lo-fi beat", input="add drums") → MUSIC
    (previous="chill lo-fi beat", input="now make hard techno") → MUSIC
    (previous="chill lo-fi beat", input="what time is it") → NOT_MUSIC

    Previous prompt: "{previous_prompt}"
    Current input: "{input}"

    Only output exactly MUSIC or NOT_MUSIC.
    """
