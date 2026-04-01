from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings

_ALLOWED_TYPES = frozenset(
    {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
    }
)
_EXT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


def _media_root() -> Path:
    root = Path(settings.MEDIA_ROOT)
    if not root.is_absolute():
        root = Path.cwd() / root
    return root.resolve()


def delete_product_image_file(image: str | None) -> None:
    if not image:
        return
    base = settings.MEDIA_URL_PATH.rstrip("/")
    if not image.startswith(base + "/"):
        return
    rel = image[len(base) :].lstrip("/")
    root = _media_root()
    target = (root / rel).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return
    if target.is_file():
        target.unlink()


async def save_product_image_file(file: UploadFile) -> str:
    ct = file.content_type or ""
    if ct not in _ALLOWED_TYPES:
        raise ValueError("Only JPEG, PNG, WebP or GIF images are allowed")

    data = await file.read()
    if len(data) > settings.MAX_UPLOAD_BYTES:
        raise ValueError(
            f"Image too large (max {settings.MAX_UPLOAD_BYTES // (1024 * 1024)} MB)",
        )

    ext = _EXT.get(ct, ".bin")
    name = f"{uuid.uuid4().hex}{ext}"
    subdir = _media_root() / "products"
    subdir.mkdir(parents=True, exist_ok=True)
    dest = subdir / name
    dest.write_bytes(data)

    return f"{settings.MEDIA_URL_PATH.rstrip('/')}/products/{name}"
