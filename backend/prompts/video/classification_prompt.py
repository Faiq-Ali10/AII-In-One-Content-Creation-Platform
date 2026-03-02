def classification_prompt_video(input: str, previous_prompt: str) -> str:
    # CASE 1: No History (Direct Intent Check)
    if not previous_prompt:
        return f"""
        You are a video intent classifier. Respond ONLY with 'VIDEO' or 'NOT_VIDEO'.
        
        ### RULES
        1. **Motion/Action**: If the input asks for movement, animation, or a video (e.g., "make it dance", "animate this", "generate a clip") -> VIDEO
        2. **Static/Still**: If the input asks for a still image, a drawing, or a photo without motion -> NOT_VIDEO
        3. **Nonsense**: Gibberish (e.g., "qwerty"), random symbols, or unreadable typos -> NOT_VIDEO
        4. **Text/General**: Conversational chat, coding, or music requests -> NOT_VIDEO
        
        ### EXAMPLES
        "make the cat walk" -> VIDEO
        "generate a 5 second clip of rain" -> VIDEO
        "draw a static house" -> NOT_VIDEO
        "asdfghjkl" -> NOT_VIDEO
        "Robot is Dancing" -> VIDEO
        "Write a poem about the sea" -> NOT_VIDEO
        
        ### INPUT
        Current Input: "{input}"
        
        Decision:
        """

    # CASE 2: With History (Contextual/Sequential Check)
    else:
        return f"""
        You are a video intent classifier. Respond ONLY with 'VIDEO' or 'NOT_VIDEO'.
        
        ### RULES
        1. **Action on Image**: If the Previous Prompt was an image description AND the Current Input asks to animate it (e.g., "make it move", "start the fire") -> VIDEO
        2. **Video Modification**: If the Previous Prompt was already a video and the input modifies the motion (e.g., "make it faster", "change the background") -> VIDEO
        3. **New Request**: If the input is a brand new request for a video, ignore history -> VIDEO
        4. **Contextual Failure**: If the input tries to "animate" something that wasn't a visual (e.g., Prev="write code", Input="animate it") -> NOT_VIDEO
        5. **Irrelevant**: General chat or non-visual tasks -> NOT_VIDEO
        
        ### EXAMPLES
        (Prev="a cat sitting", Input="make it jump") -> VIDEO
        (Prev="a car driving", Input="change the car to red") -> VIDEO
        (Prev="write a story", Input="animate the characters") -> VIDEO (Contextual shift to video)
        (Prev="hello", Input="make it faster") -> NOT_VIDEO (Nothing to make faster)
        (Prev="a static image of a tree", Input="animate the leaves") -> VIDEO
        
        ### CONTEXT
        Previous Prompt: "{previous_prompt}"
        Current Input: "{input}"

        Decision:
        """