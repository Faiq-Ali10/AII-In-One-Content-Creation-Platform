from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import cast

# Import your Video Agent
from Agents.video_agent import VideoAgent, VideoAgentState

router = APIRouter()

# Initialize Agent once (Singleton pattern)
video_agent_app = VideoAgent().get_app()

class VideoInput(BaseModel):
    input: str
    previous: str = ""
    size_choice: int = 3  # Default to 3 (Landscape/16:9) for Video

@router.post("/generate_video")
async def generate_video(data: VideoInput):
    try:
        # --- DEBUG PRINT ---
        print(f"🎥 VIDEO ROUTE RECEIVED:")
        print(f" - Input: {data.input}")
        print(f" - Previous: '{data.previous}'")
        
        # Construct the query for the Video Agent
        query = {
            "original": data.input,
            "previous": data.previous,
            "size_choice": data.size_choice
        }
        
        print(f"🎬 Video Agent: Processing '{data.input}'...")

        # Invoke the Agent
        # Note: Video generation takes time (30s+), so this might block. 
        # In production, we'd use 'ainvoke' or background tasks, but this works for now.
        response = video_agent_app.invoke(cast(VideoAgentState, query))
        
        # Check if we actually got a video back
        video_b64 = response.get("video_b64")
        
        if video_b64:
            return {
                "status": "success",
                # The Final Video
                "video_b64": video_b64,
                
                # Pro Feature: Return the "First Frame" image too!
                # This allows the UI to show a preview while loading or alongside the video.
                "image_b64": response.get("image_b64"), 
                
                # Debug Info / UI feedback
                "refined_video_prompt": response.get("refined_video_prompt"),
                "refined_image_prompt": response.get("refined_image_prompt"),
                "classified": response.get("classified")
            }
        else:
            return {
                "status": "skipped",
                "message": "We couldn't detect a clear intent for video generation. Please try verbs like 'animate', 'move', or 'dance'."
            }

    except Exception as e:
        print(f"❌ Video Error: {str(e)}")
        # Return 500 but with a clear JSON message
        return JSONResponse(
            status_code=500, 
            content={"message": f"Error generating video: {str(e)}"}
        )