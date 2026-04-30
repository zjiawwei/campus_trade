import uuid
import os
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename
from app.utils.constants import ALLOWED_IMAGE_EXTENSIONS, MAX_IMAGE_SIZE


def allowed_image(filename):
    """Check if the uploaded file has an allowed image extension."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_IMAGE_EXTENSIONS


def save_image(file, subfolder="products"):
    """Save an uploaded image file with a UUID filename.
    Returns the generated filename.
    """
    if not file or not allowed_image(file.filename):
        return None

    ext = file.filename.rsplit(".", 1)[1].lower()
    new_filename = f"{uuid.uuid4().hex}.{ext}"

    upload_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"], subfolder
    )
    os.makedirs(upload_path, exist_ok=True)

    filepath = os.path.join(upload_path, new_filename)

    # Resize large images to save storage
    img = Image.open(file)
    img.thumbnail((1200, 1200), Image.LANCZOS)
    img.save(filepath, quality=85, optimize=True)

    return new_filename


def create_thumbnail(filename, subfolder="products", size=(300, 300)):
    """Create a thumbnail for a given image filename."""
    if not filename:
        return None

    upload_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"], subfolder
    )
    filepath = os.path.join(upload_path, filename)
    if not os.path.exists(filepath):
        return None

    thumb_name = f"thumb_{filename}"
    thumb_path = os.path.join(upload_path, thumb_name)

    img = Image.open(filepath)
    img.thumbnail(size, Image.LANCZOS)
    img.save(thumb_path, quality=80, optimize=True)

    return thumb_name


def delete_image(filename, subfolder="products"):
    """Delete an image file and its thumbnail from disk."""
    if not filename:
        return

    upload_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"], subfolder
    )
    for name in [filename, f"thumb_{filename}"]:
        filepath = os.path.join(upload_path, name)
        if os.path.exists(filepath):
            os.remove(filepath)
