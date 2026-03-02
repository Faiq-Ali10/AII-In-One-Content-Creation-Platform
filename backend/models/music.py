import os
import io
import torch
import scipy.io.wavfile
import numpy as np
from transformers import AutoProcessor, MusicgenForConditionalGeneration

# --- CONFIGURATION ---
# Use "small" for speed/memory, "medium" for better quality
MODEL_ID = "facebook/musicgen-small"
device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"🎵 MusicGen configured to use: {device.upper()}")

# Global variables for lazy loading
_processor = None
_model = None

def _load_model():
    """
    Loads the MusicGen model and processor only when needed.
    Moves the model to GPU (CUDA) if available.
    """
    global _processor, _model
    
    if _processor is None:
        print(f"⏳ Loading MusicGen Processor ({MODEL_ID})...")
        _processor = AutoProcessor.from_pretrained(MODEL_ID)
        
    if _model is None:
        print(f"⏳ Loading MusicGen Model ({MODEL_ID})...")
        _model = MusicgenForConditionalGeneration.from_pretrained(MODEL_ID)
        
        # CRITICAL: Move model to GPU
        _model.to(device)
        print("✅ MusicGen Model loaded on GPU!")
        
    return _processor, _model

def generate_music(prompt: str, duration_seconds: int = 5) -> bytes:
    """
    Generates music from a text prompt.
    
    Args:
        prompt (str): Description of the music (e.g., "lo-fi hip hop beat")
        duration_seconds (int): Length of audio. 
                                Note: MusicGen generates ~50 tokens per second.
                                256 tokens ≈ 5 seconds.
    
    Returns:
        bytes: The generated WAV file as bytes.
    """
    try:
        processor, model = _load_model()
        
        # Calculate tokens based on duration (approx conversion)
        # 1 second ≈ 50 tokens
        max_new_tokens = int(duration_seconds * 50)

        # 1. Prepare Inputs & Move to GPU
        inputs = processor(
            text=[prompt], 
            padding=True, 
            return_tensors="pt"
        ).to(device) # <--- CRITICAL: Move inputs to GPU

        # 2. Generate Audio
        print(f"🎵 Generating {duration_seconds}s of audio for: '{prompt}'...")
        audio_values = model.generate(**inputs, max_new_tokens=max_new_tokens)

        # 3. Post-process & Save
        # Move back to CPU for saving to disk/memory
        sampling_rate = model.config.audio_encoder.sampling_rate
        audio_data = audio_values[0, 0].cpu().numpy()
        
        # Write to memory buffer
        buffer = io.BytesIO()
        scipy.io.wavfile.write(buffer, rate=sampling_rate, data=audio_data)
        
        return buffer.getvalue()

    except Exception as e:
        print(f"❌ Error generating music: {e}")
        raise e

# --- TEST BLOCK (Run this file directly to test) ---
if __name__ == "__main__":
    # Test generation
    wav_bytes = generate_music("80s synthwave driving music", duration_seconds=5)
    
    # Save to file to verify
    with open("test_output.wav", "wb") as f:
        f.write(wav_bytes)
    print("✅ Test complete! Saved to test_output.wav")