from PIL import Image
from modules.image_compressor import pil_to_bytes, bytes_to_pil

try:
    from rembg import remove, new_session
except ImportError:
    remove = None
    new_session = None

# Cache model sessions so they only load into memory once
_SESSIONS = {}


def get_session(model_name: str):
    if new_session is None:
        return None
    if model_name not in _SESSIONS:
        _SESSIONS[model_name] = new_session(model_name)
    return _SESSIONS[model_name]


def handle_background_removal(pil_img, model_choice: str = "Human Portrait (u2net_human_seg)"):
    if pil_img is None:
        return None

    # Map user selection to rembg model string
    model_map = {
        "Human Portrait (u2net_human_seg)": "u2net_human_seg",
        "General High Accuracy (isnet-general-use)": "isnet-general-use",
        "Standard Default (u2net)": "u2net",
    }
    
    selected_model = model_map.get(model_choice, "u2net_human_seg")
    img_bytes = pil_to_bytes(pil_img, image_format="PNG")

    if remove:
        try:
            session = get_session(selected_model)
            output_bytes = remove(
                img_bytes,
                session=session,
                alpha_matting=True,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_size=10,
            )
        except Exception:
            # Fallback if alpha matting fails on specific image types
            session = get_session(selected_model)
            output_bytes = remove(img_bytes, session=session)

        if isinstance(output_bytes, Image.Image):
            return output_bytes
        return bytes_to_pil(output_bytes)

    return pil_img