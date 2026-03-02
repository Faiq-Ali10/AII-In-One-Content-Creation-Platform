def classification_prompt_image(input: str, previous_prompt: str) -> str:
    # CASE 1: No History (Simple Check)
    if not previous_prompt:
        return f"""
        You are a Image prompt classifier. Respond only with IMAGE or NOT_IMAGE.
        
        ### RULES
        1. **Gibberish/Nonsense**: Random letters (e.g. "asdf", "kjsd"), unfinished sentences, or meaningless symbols -> NOT_IMAGE
        2. **Explicit Request**: If the input explicitly asks to see, draw, or generate a visual -> IMAGE
        3. **Irrelevant**: Generic chat ("hi", "code", "music"), questions, or text tasks -> NOT_IMAGE
        
        ### EXAMPLES
        "draw a cat" -> IMAGE
        "asdfjkl" -> NOT_IMAGE
        "make it blue" -> NOT_IMAGE (Nothing to make blue)
        
        ### INPUT
        Current Input: "{input}"
        
        Decision:
        """

    # CASE 2: With History (Contextual Check)
    else:
        return f"""
        You are a classifier. Respond only with IMAGE or NOT_IMAGE.
        
        ### RULES
        1. **Gibberish**: Random letters (e.g. "sdfg"), typos that make it unreadable -> NOT_IMAGE.
        
        2. **New Request**: If input wants a BRAND NEW image (e.g. "draw a dog instead"), ignore the previous prompt -> IMAGE.
        
        3. **Modification**: 
           - If the input tries to MODIFY the previous prompt (e.g. "make it blue"):
             - AND the Previous Prompt WAS an image description -> IMAGE.
             - BUT if the Previous Prompt was unrelated (e.g. "write code", "hello") -> NOT_IMAGE (Cannot modify non-image).
             
        4. **Irrelevant**: Conversational or text tasks -> NOT_IMAGE.
        
        ### EXAMPLES
        (Prev="draw a city", Input="make it night") -> IMAGE
        (Prev="write a poem", Input="make it rhyming") -> NOT_IMAGE
        (Prev="write a poem", Input="draw a cat") -> IMAGE (New Request overrides history)
        (Prev="draw a city", Input="hjklasdf") -> NOT_IMAGE
        
        ### CONTEXT
        Previous Prompt: "{previous_prompt}"
        Current Input: "{input}"

        Decision:
        """