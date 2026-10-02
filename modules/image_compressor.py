import io
from PIL import Image


def pil_to_bytes(pil_img, image_format="PNG"):
    if pil_img is None:
        return None
    buffer = io.BytesIO()
    if pil_img.mode in ("RGBA", "LA") and image_format.upper() in ("JPG", "JPEG"):
        pil_img = pil_img.convert("RGB")
    pil_img.save(buffer, format=image_format)
    return buffer.getvalue()


def bytes_to_pil(image_bytes):
    if not image_bytes:
        return None
    return Image.open(io.BytesIO(image_bytes))


def compress_image_handler(pil_img, quality_slider, target_format, width, height):
    if pil_img is None:
        return None, "No image uploaded."

    work_img = pil_img.copy()
    orig_w, orig_h = work_img.size

    target_w = int(width) if width and width > 0 else orig_w
    target_h = int(height) if height and height > 0 else orig_h

    if target_w != orig_w or target_h != orig_h:
        work_img = work_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    buffer = io.BytesIO()
    img_format = target_format.upper()

    if work_img.mode in ("RGBA", "P") and img_format in ("JPEG", "JPG"):
        work_img = work_img.convert("RGB")

    work_img.save(
        buffer, format=img_format, quality=int(quality_slider), optimize=True
    )
    compressed_bytes = buffer.getvalue()

    orig_buffer = io.BytesIO()
    pil_img.save(orig_buffer, format=pil_img.format or "PNG")
    orig_size_kb = len(orig_buffer.getvalue()) / 1024
    comp_size_kb = len(compressed_bytes) / 1024

    stats = (
        f"Original: {orig_w}x{orig_h}px ({orig_size_kb:.1f} KB) | "
        f"Output: {target_w}x{target_h}px ({comp_size_kb:.1f} KB) "
        f"[{((orig_size_kb - comp_size_kb) / orig_size_kb * 100):.1f}% reduction]"
    )

    return Image.open(io.BytesIO(compressed_bytes)), stats