"""Runtime detection and inference acceleration configuration."""
from app.models.schemas import RuntimeDeviceReport, InferenceConfig

def detect_runtime_device() -> RuntimeDeviceReport:
    """Detect CPU, CUDA or Apple MPS runtime."""
    try:
        import torch
        cuda=torch.cuda.is_available(); mps=hasattr(torch.backends,'mps') and torch.backends.mps.is_available()
        device='cuda' if cuda else 'mps' if mps else 'cpu'
        return RuntimeDeviceReport(device=device, cuda_available=cuda, mps_available=mps, details={'torch':torch.__version__})
    except Exception as exc:
        return RuntimeDeviceReport(device='cpu', details={'warning':str(exc)})

def recommend_inference_config(model_name, resolution, duration) -> InferenceConfig:
    """Recommend dtype/offload settings for the requested job."""
    dev=detect_runtime_device(); notes=[]
    dtype='fp16' if dev.device in {'cuda','mps'} else 'fp32'
    offload=dev.device=='cpu' or resolution in {'1080p'} or duration>8
    if offload: notes.append('enable offload/tiling for memory safety')
    return InferenceConfig(device=dev.device, dtype=dtype, offload=offload, attention_slicing=True, vae_tiling=True, notes=notes)

def apply_diffusers_optimizations(pipe, config):
    """Apply common diffusers optimization switches when available."""
    if getattr(config,'attention_slicing',False) and hasattr(pipe,'enable_attention_slicing'): pipe.enable_attention_slicing()
    if getattr(config,'vae_tiling',False) and hasattr(pipe,'enable_vae_tiling'): pipe.enable_vae_tiling()
    if getattr(config,'offload',False) and hasattr(pipe,'enable_model_cpu_offload'): pipe.enable_model_cpu_offload()
    return pipe

def estimate_generation_cost(config) -> dict:
    """Return rough cost estimate placeholders."""
    mult={'cpu':1.0,'mps':0.35,'cuda':0.2}.get(config.device,1.0)
    return {'relative_time_cost':mult, 'memory_mode':'low' if config.offload else 'normal', 'notes':config.notes}
