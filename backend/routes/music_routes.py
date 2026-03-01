from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import cast
from pydantic import BaseModel
import base64

# Import your Agent using absolute path
from Agents.music_agent import MusicAgent, AgentState

router = APIRouter()

# Initialize Agent once when the server starts
music_agent_app = MusicAgent().get_app()

class MusicInput(BaseModel):
    input: str
    previous: str

@router.post("/generate_music")
async def generate_music(data: MusicInput):
    try:
        # --- DEBUG PRINT ---
        print(f"📥 ROUTE RECEIVED:")
        print(f" - Input: {data.input}")
        print(f" - Previous: '{data.previous}'")
        query = {
            "original": data.input,
            "previous": data.previous,
        }

        print(f"🎵 Music Route: Processing '{data.input}'...")
        
        # Invoke the LangGraph Agent
        response = music_agent_app.invoke(cast(AgentState, query))
        
        music_bytes = response.get("music")

        if not music_bytes:
            return {"message": "That doesn’t look like a valid prompt. Please describe the music style or mood you’d like."}

        print("✅ Music Generated. Bytes Length:", len(music_bytes))

        # Encode music as base64 so it can be sent in JSON
        music_b64 = base64.b64encode(music_bytes).decode("utf-8")

        # Return JSON with both music and previous prompt
        return JSONResponse(content={
            "status": "success",
            "music": music_b64,
            "refined": response.get("refined")  # Update context
        })

    except Exception as e:
        print(f"❌ Music Error: {str(e)}")
        return JSONResponse(status_code=500, content={"message": "Sorry, Can't process your request."})