import logging

import numpy as np
import pandas as pd

from backend.app.services.video_preprocessing import get_tribe_model

logger = logging.getLogger(__name__)


def run_tribe_inference(events_df: pd.DataFrame) -> tuple[np.ndarray, list]:
    """
    Run TRIBE v2 brain prediction on preprocessed events.
    
    Takes the events dataframe (video + audio + text events)
    and predicts brain activity across 20,484 cortical vertices
    for each 1-second time segment.
    
    Returns:
        preds: numpy array of shape (n_segments, 20484)
        segments: list of segment objects with timing info
    """
    model = get_tribe_model()

    logger.info("Running TRIBE v2 brain prediction...")
    preds, segments = model.predict(events=events_df)

    logger.info(f"Predictions shape: {preds.shape}")
    logger.info(f"Time segments: {len(segments)}")
    logger.info(f"Brain vertices: {preds.shape[1]}")
    logger.info(f"Activation range: [{preds.min():.4f}, {preds.max():.4f}]")

    return preds, segments
