import torch
import gc

def clear_gpu_memory():
    """
    Forces a complete cleanup of the GPU memory.
    Call this BEFORE loading a heavy model like Video or Whisper.
    """
    # 1. Force Python's Garbage Collector to release unlinked objects
    gc.collect()
    
    # 2. Clear PyTorch's cache (the 'reserved' memory)
    torch.cuda.empty_cache()
    
    # 3. Optional: Sync to ensure everything is really gone
    torch.cuda.synchronize()
    
    print("🧹 GPU Memory flushed!")