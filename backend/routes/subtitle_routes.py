from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import cast

# Import your Subtitle Agent
from Agents.subtitle_agent import SubtitleAgent, SubtitleAgentState

router = APIRouter()

# Initialize Agent once
subtitle_agent_app = SubtitleAgent().get_app()

class SubtitleInput(BaseModel):
    video_b64: str
    original_filename: str
    subtitle_type: int = 1  # Default to 1 for Inline
    position: str = "bottom" # Added position parameter with a default

@router.post("/add_subtitles")
async def add_subtitles(data: SubtitleInput):
    try:
        # *** DEBUG PRINT ***
        print(f"📥 ROUTE RECEIVED: /add_subtitles")
        print(f" * Filename: {data.original_filename}")
        print(f" * Type: {data.subtitle_type}")
        print(f" * Position: {data.position}")
        
        query = {
            "video_b64": data.video_b64,
            "original_filename": data.original_filename,
            "subtitle_type": data.subtitle_type,
            "position": data.position
        }
        
        print(f"🎬 Subtitle Route: Processing video...")

        # Invoke the Agent
        response = subtitle_agent_app.invoke(cast(SubtitleAgentState, query))
        
        subtitled_video_b64 = response.get("subtitled_video_b64")
        
        if subtitled_video_b64:
            return {
                "status": "success",
                "subtitled_video_b64": subtitled_video_b64,
                "message": response.get("message", "Subtitles successfully added.")
            }
        else:
            return {
                "status": "error",
                "message": response.get("message", "Failed to generate subtitles.")
            }

    except Exception as e:
        print(f"❌ Subtitle Error: {str(e)}")
        return JSONResponse(status_code=500, content={"message": "Error processing subtitle request."})