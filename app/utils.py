import os
import uuid

from flask import current_app
from PIL import Image

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
MAX_DIMENSION = 1200


def _allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_image(file_storage):
    """Save an uploaded image (resized to max 1200px) and return its path
    relative to the static folder, or None if no/invalid file was given."""
    if not file_storage or not file_storage.filename:
        return None
    if not _allowed(file_storage.filename):
        return None

    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    if ext == "jpeg":
        ext = "jpg"
    new_name = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    full_path = os.path.join(upload_dir, new_name)

    img = Image.open(file_storage.stream)
    img.thumbnail((MAX_DIMENSION, MAX_DIMENSION))

    save_kwargs = {}
    if ext == "jpg":
        if img.mode != "RGB":
            img = img.convert("RGB")
        save_kwargs.update(quality=85, optimize=True)

    img.save(full_path, **save_kwargs)

    return f"uploads/{new_name}"
