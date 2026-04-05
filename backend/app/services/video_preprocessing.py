import logging
from pathlib import Path

import pandas as pd

from backend.app.config import CACHE_DIR, TRIBE_MODEL_ID, TRIBE_DEVICE

logger = logging.getLogger(__name__)


def get_tribe_model():
    """Load TRIBE v2 model. Cached after first call."""
    from tribev2 import TribeModel

    device_overrides = {
        "data.text_feature.device": TRIBE_DEVICE,
        "data.audio_feature.device": TRIBE_DEVICE,
        "data.video_feature.image.device": TRIBE_DEVICE,
        "data.image_feature.image.device": TRIBE_DEVICE,
        "data.num_workers": 0,
    }

    logger.info("Loading TRIBE v2 model...")
    model = TribeModel.from_pretrained(
        TRIBE_MODEL_ID,
        cache_folder=str(CACHE_DIR),
        device=TRIBE_DEVICE,
        config_update=device_overrides,
    )
    logger.info("TRIBE v2 model loaded successfully")
    return model


def preprocess_video(video_path: str) -> pd.DataFrame:
    """
    Preprocess video into events dataframe.
    
    Extracts:
    1. Video frames for V-JEPA2
    2. Audio track for Wav2Vec-BERT  
    3. Word-level transcript for Llama 3.2
    
    Returns events dataframe ready for TRIBE v2 inference.
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    logger.info(f"Preprocessing video: {video_path.name}")

    model = get_tribe_model()

    logger.info("Building events dataframe (extracting audio, transcribing speech)...")
    events_df = model.get_events_dataframe(video_path=str(video_path))

    logger.info(f"Events dataframe built: {events_df.shape[0]} events, {events_df.shape[1]} columns")
    logger.info(f"Event types: {events_df['type'].value_counts().to_dict()}")

    return events_df
