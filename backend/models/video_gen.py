import os
import base64
import io
import torch
import tempfile
from diffusers import I2VGenXLPipeline
from diffusers.utils import export_to_video, load_image

# --- GLOBAL MODEL LOADING (Run this once at the top of your script) ---
# We load the model here so it stays in GPU memory
print("⏳ Loading I2VGen-XL Model...")
pipe = I2VGenXLPipeline.from_pretrained(
    "ali-vilab/i2vgen-xl", 
    torch_dtype=torch.float16, 
    variant="fp16"
)
pipe.enable_model_cpu_offload() # CRITICAL: Saves VRAM on Kaggle T4 GPUs
print("✅ Model Loaded!")

def generate_video_from_image_base64(image_b64: str, prompt: str) -> str:
    """
    Takes a base64 image + prompt, generates video using local I2VGen-XL model,
    and returns base64 video.
    """
    try:
        # 1. Decode Base64 string to Pillow Image
        if "," in image_b64:
            image_b64 = image_b64.split(",")[1]
        
        input_image_bytes = base64.b64decode(image_b64)
        image = load_image(io.BytesIO(input_image_bytes))
        
        # 2. Resize Image (I2VGen-XL works best at specific resolutions)
        # We resize to 1280x720 to match the model's training data and prevent errors
        image = image.resize((1280, 720))

        # 3. Generate Video Frames
        # num_inference_steps=50 gives good quality. Lower to 30 for speed.
        # guidance_scale=9.0 helps the model stick to your text prompt.
        print(f"🎬 Generating video for prompt: {prompt}")
        frames = pipe(
            prompt=prompt,
            image=image,
            num_inference_steps=50,
            guidance_scale=9.0,
            generator=torch.manual_seed(42) # Optional: Makes results reproducible
        ).frames[0]

        # 4. Export Video to a temporary file
        # We need a physical file to read back bytes for Base64
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_file:
            temp_path = tmp_file.name
            
        export_to_video(frames, temp_path, fps=16)

        # 5. Read file bytes and encode to Base64
        with open(temp_path, "rb") as f:
            video_bytes = f.read()
            
        video_b64 = base64.b64encode(video_bytes).decode("utf-8")
        
        # Cleanup temp file
        os.remove(temp_path)
        
        return video_b64

    except Exception as e:
        print(f"Error in I2VGen-XL generation: {e}")
        raise e