import streamlit as st
import requests
import base64
import os
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
API_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api") 

st.set_page_config(
    page_title="AI Creative Studio",
    page_icon="🎬",
    layout="centered"
)

# --- CSS for Styling ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- GLOBAL MEMORY INITIALIZATION ---
if "music_context" not in st.session_state:
    st.session_state.music_context = ""

if "image_context" not in st.session_state:
    st.session_state.image_context = ""

if "video_context" not in st.session_state:
    st.session_state.video_context = ""

# --- Helper Functions: Clear Input Callbacks ---
def clear_music_input():
    st.session_state["music_temp"] = st.session_state.music_input
    st.session_state.music_input = ""

def clear_image_input():
    st.session_state["image_temp"] = st.session_state.image_input
    st.session_state.image_input = ""

def clear_video_input():
    st.session_state["video_temp"] = st.session_state.video_input
    st.session_state.video_input = ""

# ==========================================
# 🎵 MUSIC GENERATION UI
# ==========================================
def render_music_ui():
    st.header("🎵 AI Music Generator")
    st.caption("Describe the mood, instruments, or genre.")

    with st.form(key="music_form", clear_on_submit=False):
        st.text_area(
            "Music Prompt", 
            height=100, 
            placeholder="Example: Lo-fi hip hop beat for studying...",
            key="music_input"
        )
        submit_button = st.form_submit_button(label="Generate Music", on_click=clear_music_input)

    if submit_button:
        prompt_to_use = st.session_state.get("music_temp", "")
        if not prompt_to_use: return

        st.info(f"🎵 Composing: **{prompt_to_use}**")

        with st.spinner("🎧 Generating audio... (30-60s)"):
            try:
                payload = {"input": prompt_to_use, "previous": st.session_state.music_context}
                response = requests.post(f"{API_BASE_URL}/generate_music", json=payload, verify=False)
                
                if response.status_code == 200:
                    data = response.json()
                    if "music" in data and data["music"]:
                        st.session_state.music_context = data.get("refined") or data.get("previous") or ""
                        music_bytes = base64.b64decode(data["music"])
                        
                        st.success("✨ Composition Complete!")
                        st.audio(music_bytes, format='audio/wav')
                        st.download_button("⬇️ Download Track", music_bytes, "music.wav", "audio/wav")
                        
                        with st.expander("👀 Agent Details"):
                            st.write(f"**Refined Prompt:** {st.session_state.music_context}")
                    else:
                        st.warning(f"⚠️ {data.get('message', 'No audio returned.')}")
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# ==========================================
# 🎨 IMAGE GENERATION UI
# ==========================================
def render_image_ui():
    st.header("🎨 AI Image Generator")
    st.caption("Create stunning visuals from text.")

    with st.form(key="image_form", clear_on_submit=False):
        st.text_area(
            "Image Prompt", 
            height=100, 
            placeholder="Example: A futuristic city with neon rain...",
            key="image_input"
        )
        col1, col2 = st.columns(2)
        with col1:
            size_label = st.selectbox("Aspect Ratio", ["Landscape (16:9)", "Square (1:1)", "Portrait (9:16)"])
        
        submit_button = st.form_submit_button(label="Generate Image", on_click=clear_image_input)

    if submit_button:
        prompt_to_use = st.session_state.get("image_temp", "")
        if not prompt_to_use: return

        size_map = {"Square (1:1)": 1, "Portrait (9:16)": 2, "Landscape (16:9)": 3}
        choice = size_map[size_label]

        st.info(f"🎨 Painting: **{prompt_to_use}**")

        with st.spinner("🖌️ Painting..."):
            try:
                payload = {
                    "input": prompt_to_use, 
                    "previous": st.session_state.image_context, 
                    "size_choice": choice
                }
                response = requests.post(f"{API_BASE_URL}/generate_image", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    if "image_b64" in data:
                        st.session_state.image_context = data.get("refined", "")
                        image_bytes = base64.b64decode(data["image_b64"])
                        
                        st.success("✨ Image Generated!")
                        st.image(image_bytes, use_container_width=True)
                        st.download_button("⬇️ Download Image", image_bytes, "image.jpg", "image/jpeg")
                        
                        with st.expander("👀 Agent Details"):
                            st.write(f"**Refined Prompt:** {data.get('refined')}")
                    else:
                        st.warning(f"⚠️ {data.get('message', 'No image returned.')}")
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# ==========================================
# 🎬 VIDEO GENERATION UI (NEW)
# ==========================================
def render_video_ui():
    st.header("🎬 AI Video Director")
    st.caption("Turn text or ideas into cinematic 16:9 video.")

    with st.form(key="video_form", clear_on_submit=False):
        st.text_area(
            "Video Prompt", 
            height=100, 
            placeholder="Example: A cyber cat dancing in the rain, cinematic lighting...",
            key="video_input"
        )
        # Video models usually prefer Landscape, so we default to that or hide the option
        st.caption("ℹ️ Note: Videos are generated in **Landscape (16:9)** for best results.")
        
        submit_button = st.form_submit_button(label="Generate Video", on_click=clear_video_input)

    if submit_button:
        prompt_to_use = st.session_state.get("video_temp", "")
        if not prompt_to_use: 
            st.warning("Please enter a prompt first.")
            return

        st.info(f"🎬 Directing: **{prompt_to_use}**")

        # Video generation takes longer, so we give a specific spinner message
        with st.spinner("🍿 Lights, Camera, Action... (This can take 60-90 seconds)"):
            try:
                # 1. Send Context (Memory)
                payload = {
                    "input": prompt_to_use, 
                    "previous": st.session_state.video_context,
                    "size_choice": 2 # Default to Landscape for video
                }
                
                response = requests.post(f"{API_BASE_URL}/generate_video", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "video_b64" in data:
                        # 2. Update Context (Save Memory)
                        st.session_state.video_context = data.get("refined_video_prompt", "")

                        # Decode Assets
                        video_bytes = base64.b64decode(data["video_b64"])
                        
                        st.success("✨ Cut! Video is ready.")

                        # --- PRO FEATURE: Display First Frame Poster ---
                        if "image_b64" in data and data["image_b64"]:
                            image_bytes = base64.b64decode(data["image_b64"])
                            st.subheader("🖼️ First Frame (Preview)")
                            st.image(image_bytes, caption="Generated Base Frame", use_container_width=True)
                            
                            # Download option for the image too
                            st.download_button(
                                label="⬇️ Download Poster Image",
                                data=image_bytes,
                                file_name="video_poster.jpg",
                                mime="image/jpeg",
                                key="dl_poster"
                            )

                        # --- Display Video ---
                        st.subheader("🎥 Final Video")
                        st.video(video_bytes)
                        
                        st.download_button(
                            label="⬇️ Download Video (MP4)",
                            data=video_bytes,
                            file_name="generated_video.mp4",
                            mime="video/mp4",
                            key="dl_video"
                        )
                        
                        with st.expander("👀 Director's Notes (Agent Details)"):
                            st.write(f"**Refined Image Prompt:** {data.get('refined_image_prompt')}")
                            st.write(f"**Refined Motion Prompt:** {data.get('refined_video_prompt')}")
                    else:
                        msg = data.get("message", "No video returned.")
                        st.warning(f"⚠️ {msg}")
                else:
                    st.error(f"Server Error: {response.status_code} - {response.text}")
            
            except Exception as e:
                st.error(f"Connection Error: {e}")

# ==========================================
# 🎛️ MAIN APP LOGIC
# ==========================================
def main():
    st.sidebar.title("🎛️ Control Panel")
    
    # Mode Selector
    mode = st.sidebar.radio(
        "Choose Mode:",
        ["Music Generator", "Image Generator", "Video Generator"],
        index=0 
    )

    # Debugger
    with st.sidebar.expander("🧠 Memory Debugger", expanded=False):
        st.write(f"**Music Memory:** '{st.session_state.music_context}'")
        st.write(f"**Image Memory:** '{st.session_state.image_context}'")
        st.write(f"**Video Memory:** '{st.session_state.video_context}'")

    st.sidebar.markdown("---")
    st.sidebar.info("Powered by **Groq**, **HuggingFace**, **Fal.ai** & **MusicGen**.")

    if mode == "Music Generator":
        render_music_ui()
    elif mode == "Image Generator":
        render_image_ui()
    elif mode == "Video Generator":
        render_video_ui()

if __name__ == "__main__":
    main()