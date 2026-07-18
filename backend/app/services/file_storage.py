import uuid
from pathlib import Path

from app.config import settings

UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_upload(file_bytes: bytes, original_filename: str) -> str:
    """
    Saves the uploaded file to local disk with a random filename (avoids
    collisions and avoids trusting the original filename). Returns the
    saved path, stored as Report.file_url.

    NOTE: local disk storage is fine for the hackathon build, but doesn't
    survive a container rebuild unless the upload directory is mounted as a
    volume. Before real deployment, swap this for S3 or similar cloud
    storage - the function signature can stay the same, only the inside
    needs to change.
    """
    ext = Path(original_filename).suffix
    unique_name = f"{uuid.uuid4()}{ext}"
    dest = UPLOAD_DIR / unique_name
    dest.write_bytes(file_bytes)
    return str(dest)