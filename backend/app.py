import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 1. Load Environment Variables GLOBALLY (First thing to do)
load_dotenv()
os.environ["GROQ_API_KEY"] = str(os.getenv("GROQ_API_KEY"))
os.environ["GOOGLE_API_KEY"] = str(os.getenv("GOOGLE_API_KEY"))

# 2. Import your clean routers
from routes import music_routes
from routes import image_routes
from routes import subtitle_routes 

app = FastAPI()

# 3. Setup CORS (Crucial for Frontend to talk to Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Connect the Routers
# This adds all endpoints from the other files to this app
app.include_router(music_routes.router, prefix="/api", tags=["Music"])
app.include_router(image_routes.router, prefix="/api", tags=["Image"])
app.include_router(subtitle_routes.router, prefix="/api", tags=["Subtitle"])

@app.get("/")
def read_root():
    return {
        "status": "Online", 
        "endpoints": ["/api/generate_music", "/api/generate_image"]
    }