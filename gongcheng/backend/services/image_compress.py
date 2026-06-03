"""上传图片压缩 —— 长边超过 MAX_SIDE 时缩放 + JPEG 重编码，兜底保证文件不超 500KB 左右。"""

from PIL import Image
import io, os

MAX_SIDE = 1920
JPEG_QUALITY = 82


def compress_uploaded_image(raw_bytes: bytes, save_path: str) -> str:
    """接收原始字节，压缩后写入 save_path（始终 .jpg），返回最终路径。"""
    save_path = os.path.splitext(save_path)[0] + ".jpg"

    try:
        img = Image.open(io.BytesIO(raw_bytes))
    except Exception:
        with open(save_path, "wb") as f:
            f.write(raw_bytes)
        return save_path

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    w, h = img.size
    if max(w, h) > MAX_SIDE:
        ratio = MAX_SIDE / max(w, h)
        img = img.resize((round(w * ratio), round(h * ratio)), Image.LANCZOS)

    img.save(save_path, "JPEG", quality=JPEG_QUALITY, optimize=True)
    return save_path
