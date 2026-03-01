from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import cast

# Import your Image Agent
from Agents.image_agent import ImageAgent, AgentState

router = APIRouter()

# Initialize Agent once
image_agent_app = ImageAgent().get_app()

class ImageInput(BaseModel):
    input: str
    previous: str = ""
    size_choice: int = 3  # Default to Landscape

@router.post("/generate_image")
async def generate_image(data: ImageInput):
    try:
        # --- DEBUG PRINT ---
        print(f"📥 ROUTE RECEIVED:")
        print(f" - Input: {data.input}")
        print(f" - Previous: '{data.previous}'")
        query = {
            "original": data.input,
            "previous": data.previous,
            "size_choice": data.size_choice
        }
        
        print(f"🎨 Image Route: Processing '{data.input}'...")

        # Invoke the Agent
        # We cast to AgentState to keep type checkers happy, though not strictly needed at runtime
        response = image_agent_app.invoke(cast(AgentState, query))
        
        # --- FIX: Look for 'image_b64', NOT 'image_url' ---
        # The agent now returns base64 data to handle the API key securely
        image_b64 = response.get("image_b64")
        
        if image_b64:
            return {
                "status": "success",
                "image_b64": image_b64,  # <--- Send this key!
                "refined": response.get("refined"),
                "classified": response.get("classified")
            }
        else:
            return {
                "status": "skipped",
                "message": "That doesn't look like a valid image prompt. Please describe a visual scene (e.g., 'A sunset', 'Cyberpunk city') or explicitly ask to 'draw' something."
            }

    except Exception as e:
        print(f"❌ Image Error: {str(e)}")
        return JSONResponse(status_code=500, content={"message": "Error processing image request."})