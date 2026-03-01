import streamlit as st
import requests
import base64
import os
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
# Default to localhost if .env is missing
API_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api") 

st.set_page_config(
    page_title="AI Creative Studio",
    page_icon="🎹",
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
# We initialize this at the top level so it persists across re-runs
if "music_context" not in st.session_state:
    st.session_state.music_context = ""

if "image_context" not in st.session_state:
    st.session_state.image_context = ""

# --- Helper Functions: Clear Input Callbacks ---
def clear_music_input():
    st.session_state["music_temp"] = st.session_state.music_input
    st.session_state.music_input = ""

def clear_image_input():
    st.session_state["image_temp"] = st.session_state.image_input
    st.session_state.image_input = ""

# ==========================================
# 🎵 MUSIC GENERATION UI
# ==========================================
def render_music_ui():
    st.header("🎵 AI Music Generator")
    st.caption("Describe the mood, instruments, or genre.")

    # --- FORM ---
    with st.form(key="music_form", clear_on_submit=False):
        st.text_area(
            "Music Prompt", 
            height=100, 
            placeholder="Example: Lo-fi hip hop beat for studying, chill vibes...",
            key="music_input"
        )
        submit_button = st.form_submit_button(label="Generate Music", on_click=clear_music_input)

    # --- LOGIC ---
    if submit_button:
        prompt_to_use = st.session_state.get("music_temp", "")

        if not prompt_to_use:
            st.warning("Please enter a prompt first.")
            return

        st.info(f"🎵 Composing: **{prompt_to_use}**")

        with st.spinner("🎧 Generating audio... (This may take 30-60s)"):
            try:
                # 1. Send Context (Memory)
                payload = {
                    "input": prompt_to_use, 
                    "previous": st.session_state.music_context
                }
                
                response = requests.post(f"{API_BASE_URL}/generate_music", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "music" in data and data["music"]:
                        # 2. Update Context (Save Memory)
                        # Handle cases where backend might send 'refined' OR 'previous'
                        new_memory = data.get("refined") or data.get("previous") or ""
                        st.session_state.music_context = new_memory
                        
                        # Decode & Play
                        music_bytes = base64.b64decode(data["music"])
                        st.success("✨ Composition Complete!")
                        st.audio(music_bytes, format='audio/wav')
                        
                        # Download
                        st.download_button(
                            label="⬇️ Download Track",
                            data=music_bytes,
                            file_name="generated_music.wav",
                            mime="audio/wav"
                        )
                        
                        with st.expander("👀 See Agent Details"):
                            st.write(f"**Refined Prompt:** {new_memory}")
                            st.write(f"**Memory Used:** {payload['previous'] if payload['previous'] else 'None'}")
                    else:
                        # Display Backend Message (e.g., "Not a music prompt")
                        msg = data.get("message", "No audio data returned.")
                        st.warning(f"⚠️ {msg}")
                else:
                    st.error(f"Server Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                st.error(f"Connection Error: {e}")

# ==========================================
# 🎨 IMAGE GENERATION UI
# ==========================================
def render_image_ui():
    st.header("🎨 AI Image Generator")
    st.caption("Create stunning visuals from text.")

    # --- FORM ---
    with st.form(key="image_form", clear_on_submit=False):
        st.text_area(
            "Image Prompt", 
            height=100, 
            placeholder="Example: A futuristic city with neon rain, 8k resolution...",
            key="image_input"
        )

        col1, col2 = st.columns(2)
        with col1:
            size_label = st.selectbox("Aspect Ratio", ["Landscape (16:9)", "Square (1:1)", "Portrait (9:16)"])
        
        submit_button = st.form_submit_button(label="Generate Image", on_click=clear_image_input)

    # --- LOGIC ---
    if submit_button:
        prompt_to_use = st.session_state.get("image_temp", "")
        
        size_map = {"Square (1:1)": 1, "Portrait (9:16)": 2, "Landscape (16:9)": 3}
        choice = size_map[size_label]

        if not prompt_to_use:
            st.warning("Please enter a prompt first.")
            return

        st.info(f"🎨 Painting: **{prompt_to_use}**")

        with st.spinner("🖌️ Painting your masterpiece..."):
            try:
                # 1. Send Context (Memory)
                payload = {
                    "input": prompt_to_use, 
                    "previous": st.session_state.image_context, 
                    "size_choice": choice
                }
                
                response = requests.post(f"{API_BASE_URL}/generate_image", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "image_b64" in data and data["image_b64"]:
                        # 2. Update Context (Save Memory)
                        st.session_state.image_context = data.get("refined", "")

                        # Decode & Display
                        image_bytes = base64.b64decode(data["image_b64"])
                        
                        st.success("✨ Image Generated!")
                        st.image(image_bytes, use_container_width=True)
                        
                        # Download
                        st.download_button(
                            label="⬇️ Download Image",
                            data=image_bytes,
                            file_name="generated_image.jpg",
                            mime="image/jpeg"
                        )
                        
                        with st.expander("👀 See Agent Details"):
                            st.write(f"**Refined Prompt:** {data.get('refined', 'N/A')}")
                            st.write(f"**Memory Used:** {payload['previous'] if payload['previous'] else 'None'}")
                    else:
                        # Display Backend Message (e.g., "Not an image prompt")
                        msg = data.get("message", "The agent decided not to generate an image.")
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
    
    # Debugger to confirm memory is holding
    with st.sidebar.expander("🧠 Memory Debugger", expanded=False):
        st.write(f"**Music Memory:** '{st.session_state.music_context}'")
        st.write(f"**Image Memory:** '{st.session_state.image_context}'")

    mode = st.sidebar.radio(
        "Choose Mode:",
        ["Music Generator", "Image Generator"],
        index=0 
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("Powered by **Groq**, **HuggingFace**, and **MusicGen**.")

    if mode == "Music Generator":
        render_music_ui()
    else:
        render_image_ui()

if __name__ == "__main__":
    main()