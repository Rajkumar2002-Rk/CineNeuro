import uuid
import logging
from pathlib import Path

import aiofiles
from fastapi import UploadFile, HTTPException

from backend.app.config import (
    UPLOAD_DIR,
    MAX_FILE_SIZE_BYTES,
    MAX_FILE_SIZE_MB,
    ALLOWED_VIDEO_EXTENSIONS,
    ALLOWED_CONTENT_TYPES,
)

logger = logging.getLogger(__name__)


async def validate_video_file(file: UploadFile) -> None:
    """Validate uploaded file is a real video within size limits."""

    # Check file extension
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{suffix}'. Allowed: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}",
        )

    # Check content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid content type '{file.content_type}'. Must be a video file.",
        )

    # Check file size by reading first chunk
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({file_size / 1024 / 1024:.1f}MB). Maximum is {MAX_FILE_SIZE_MB}MB.",
        )

    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="Empty file uploaded.",
        )


async def save_video_locally(file: UploadFile, job_id: str) -> Path:
    """Save uploaded video to local storage. Returns the saved file path."""

    suffix = Path(file.filename).suffix.lower()
    save_path = UPLOAD_DIR / f"{job_id}{suffix}"

    async with aiofiles.open(save_path, "wb") as out_file:
        while chunk := await file.read(1024 * 1024):
            await out_file.write(chunk)

    logger.info(f"Saved video to {save_path} ({save_path.stat().st_size / 1024 / 1024:.1f}MB)")
    return save_path


def generate_job_id() -> str:
    """Generate a unique job ID for tracking analysis."""
    return str(uuid.uuid4())
