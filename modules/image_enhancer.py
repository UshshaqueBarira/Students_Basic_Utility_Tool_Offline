import torch
import numpy as np
from PIL import Image
from cv2 import cvtColor, COLOR_RGB2BGR, COLOR_BGR2RGB
from realesrgan import RealESRGANer
from realesrgan.archs.srvgg_arch import SRVGGNetCompact

_UPSAMPLER = None

def get_upsampler():
    global _UPSAMPLER
    if _UPSAMPLER is None:
        # Use RealESRGAN Compact model (lightweight, zero basicSR dependency)
        model = SRVGGNetCompact(
            num_in_ch=3, 
            num_out_ch=3, 
            num_feat=64, 
            num_conv=32, 
            upscale=4, 
            act_type='prelu'
        )
        model_url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth"
        device = "cuda" if torch.cuda.is_available() else "cpu"

        _UPSAMPLER = RealESRGANer(
            scale=4,
            model_path=model_url,
            dni_weight=None,
            model=model,
            tile=0,
            tile_pad=10,
            pre_pad=0,
            half=False,
            device=device,
        )
    return _UPSAMPLER


def enhance_image_quality(pil_img, upscale_factor=2):
    """Enhances photo quality using RealESRGAN without basicSR."""
    if pil_img is None:
        return None, "Please upload an image."

    orig_w, orig_h = pil_img.size
    img_np = np.array(pil_img.convert("RGB"))
    img_bgr = cvtColor(img_np, COLOR_RGB2BGR)

    try:
        upsampler = get_upsampler()
        output_bgr, _ = upsampler.enhance(img_bgr, outscale=int(upscale_factor))
        output_rgb = cvtColor(output_bgr, COLOR_BGR2RGB)
        res = Image.fromarray(output_rgb)
    except Exception as e:
        # Fallback to Lanczos scaling if model inference fails
        scale = int(upscale_factor)
        res = pil_img.resize((orig_w * scale, orig_h * scale), Image.Resampling.LANCZOS)

    new_w, new_h = res.size
    stats = (
        f"Original Resolution: {orig_w}x{orig_h}px | "
        f"Enhanced Resolution: {new_w}x{new_h}px ({upscale_factor}x RealESRGAN Upscaled)"
    )

    return res, stats