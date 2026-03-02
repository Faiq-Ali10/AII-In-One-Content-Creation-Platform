def refine_prompt_image_for_video(input: str, previous: str) -> str:
    # CASE 1: No History (Create the Perfect Keyframe)
    if not previous:
        return f"""
        You are an expert Pre-visualization Artist for Movies. 
        Your task is to write a prompt for a STATIC IMAGE that will later be animated into a video.

        ### CRITICAL VIDEO-BASE RULES
        1. **COMPOSITION**: Force "Cinematic Wide Shot", "16:9 Aspect Ratio", "Widescreen". 
           *Reason: Video models hallucinate if the image is square or vertical.*
        2. **FRAMING**: Ensure the subject has "headroom" and "lead room" (space to move into). Avoid extreme close-ups.
        3. **CLARITY**: Use "Sharp focus", "High fidelity". 
           *Reason: Video generation naturally adds blur; starting with a blurry image ruins the video.*
        4. **NO MOTION**: Describe the scene as "frozen in time" but *ready* for action. Do not use words like "blur" or "streaks" yet (that's for the video model).
        5. **LIGHTING**: Use "Cinematic lighting", "Volumetric fog", or "Backlighting" to separate the subject from the background.

        ### EXAMPLES
        User: "a cat dancing"
        → "A cinematic wide shot of a fluffy ginger cat standing on a disco floor, 16:9, sharp focus, volumetric stage lighting, room for movement, highly detailed, photorealistic."

        User: "car drifting"
        → "A sleek black sports car positioned on a wet neon highway at night, cinematic wide angle, 16:9, sharp details, reflections on pavement, hyper-realistic, 8k."

        ### INPUT
        User Input: "{input}"
        
        Refined Prompt:
        """

    # CASE 2: With History (Contextual Modification for Video Base)
    else:
        return f"""
        You are an expert Pre-visualization Artist.
        The user wants to modify an existing image concept to serve as a better base for a video.

        ### RULES
        1. **Keep it Cinematic**: Whatever the user changes, ensure the result remains "Widescreen" and "High Resolution".
        2. **Subject Consistency**: If modifying a previous prompt, keep the core identity (colors, style) unless told otherwise.
        3. **Action Readiness**: If the user says "make it run", ensure the new image places the subject on a surface where running is possible (e.g., a road, not floating in void).

        Previous Prompt: "{previous}"
        User Update: "{input}"

        Refined Video-Ready Image Prompt:
        """