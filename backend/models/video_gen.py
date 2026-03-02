import os
import base64
import io
import torch
import tempfile
from PIL import Image
from diffusers import I2VGenXLPipeline
from diffusers.utils import export_to_video
from utils.memory_utils import clear_gpu_memory 

# Global variable to hold the model
pipe = None

def _load_model():
    global pipe
    if pipe is None:
        # 1. CRITICAL: Clear memory before loading this giant model
        clear_gpu_memory() 
        
        print("⏳ Loading I2VGen-XL Model...")
        pipe = I2VGenXLPipeline.from_pretrained(
            "ali-vilab/i2vgen-xl", 
            torch_dtype=torch.float16, 
            variant="fp16"
        )
        # Enable CPU Offload (Essential for T4)
        pipe.enable_model_cpu_offload()
        print("✅ I2VGen-XL Model Loaded!")
    return pipe

def generate_video_from_image_base64(image_b64: str, prompt: str) -> str:
    try:
        # Load model (with memory clearing)
        pipeline = _load_model()

        # ... (Image decoding logic stays the same) ...
        if "," in image_b64:
            image_b64 = image_b64.split(",")[1]
        input_image_bytes = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(input_image_bytes)).convert("RGB")
        image = image.resize((1280, 720))

        print(f"🎬 Generating video for prompt: {prompt}")
        
        # --- OPTIMIZATION IS HERE ---
        frames = pipeline(
            prompt=prompt,
            image=image,
            # CHANGE FROM 50 TO 25 or 30
            # 50 steps = ~3 mins (Timeout risk)
            # 30 steps = ~1.5 mins (Much safer)
            num_inference_steps=30, 
            guidance_scale=9.0,
            generator=torch.manual_seed(42)
        ).frames[0]

        # ... (Export logic stays the same) ...
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_file:
            temp_path = tmp_file.name 
        export_to_video(frames, temp_path, fps=16)
        
        with open(temp_path, "rb") as f:
            video_bytes = f.read() 
        video_b64 = base64.b64encode(video_bytes).decode("utf-8")
        os.remove(temp_path)
        
        return video_b64

    except Exception as e:
        print(f"❌ Error in I2VGen-XL generation: {e}")
        # If it crashes, clear memory so the next try might work
        clear_gpu_memory()
        raise e